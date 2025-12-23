import frappe
import json

from frappe import _
from frappe.utils import now_datetime
from frappe.desk.form.assign_to import add as assign_to_user
from frappe.desk.form.assign_to import clear as clear_all_assignments
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket, get_customer, is_admin, is_agent

class HDTicketOverride(HDTicket):

	def on_update(self):
		'''Extend on_update to auto-assign when ticket is Open.'''

		super().on_update()
		if self.agent_group and self.status == 'Open':
			self.handle_assignment_by_team()

		if self.status == 'Closed':
			# Clear all assignments on ticket close
			clear_all_assignments(self.doctype, self.name)

	def before_save(self):
		super().before_save()
		self.set_missing_values()

	def validate(self):
		'''
			Extend validate to set agent group automatically.
		'''
		super().validate()
		self.set_missing_values()

	def set_missing_values(self):
		'''
			Set missing values before saving, for manual ticket creation.
		'''
		#Set raised_by and requested_employee from session user if not created via EMAIL
		if not self.email_account:
			if not self.requested_employee:
				if frappe.db.exists('Employee', {'user_id': frappe.session.user}):
					self.requested_employee = frappe.db.get_value('Employee', {'user_id': frappe.session.user})
			if not self.raised_by:
				self.raised_by = frappe.session.user

		#Set requested_employee from raised_by if available from EMAIL
		if self.raised_by and not self.requested_employee:
			if frappe.db.exists('Employee', {'user_id': self.raised_by}):
				self.requested_employee = frappe.db.get_value('Employee', {'user_id': self.raised_by})

		#Set values from requested_employee if available
		if self.requested_employee:
			if frappe.db.get_value('Employee', self.requested_employee , 'user_id'):
				self.raised_by = frappe.db.get_value('Employee', self.requested_employee , 'user_id')
			if not self.employee_name:
				self.employee_name = frappe.db.get_value('Employee', self.requested_employee , 'employee_name')
			if not self.reports_to:
				self.reports_to = frappe.db.get_value('Employee', self.requested_employee , 'reports_to')
			if self.reports_to and not self.reports_to_email:
				self.reports_to_email = frappe.db.get_value('Employee', self.reports_to , 'user_id')
		self.set_agent_group()

	def handle_assignment_by_team(self):
		'''Assign ticket to all active agents in the selected agent group.'''

		if not self.agent_group:
			return

		if not frappe.db.exists('HD Team', self.agent_group):
			return

		prev_doc = self.get_doc_before_save()
		do_assign = False
		if prev_doc and prev_doc.agent_group != self.agent_group:
			do_assign = True
			# Clear all previous assignments
			clear_all_assignments(self.doctype, self.name)
		elif prev_doc:
			do_assign = False
		else:
			do_assign = True

		if do_assign:
			# Fetch all active users from the team
			active_users = self.get_active_users_from_team(self.agent_group)

			if not active_users:
				return

			# Assign to all active agents
			for user in active_users:
				existing_todo = frappe.db.exists('ToDo', {
					'reference_type': self.doctype,
					'reference_name': self.name,
					'allocated_to': user,
					'status': ['!=', 'Cancelled'],
				})

				if not existing_todo:
					assign_to_user({
						'doctype': self.doctype,
						'name': self.name,
						'assign_to': [user],
						'description': f'You have been assigned a ticket by  team {self.agent_group}',
					})

	def get_active_users_from_team(self, team_name):
		'''Return active users (User IDs) from HD Team based on active HD Agent mapping.'''

		if not frappe.db.exists('HD Team', team_name):
			return []

		team = frappe.get_doc('HD Team', team_name)
		team_users = [row.user for row in team.users if row.user]

		if not team_users:
			return []

		# Fetch user + is_active for each agent
		agents = frappe.get_all(
			'HD Agent',
			filters={'user': ['in', team_users]},
			fields=['user', 'is_active']
		)
		# Return only the active ones
		active_users = [agent.user for agent in agents if agent.is_active == 1]
		return active_users


	def set_agent_group(self):
		'''Set agent_group directly from HD Team or fallback to default team.'''

		if self.agent_group:
			return

		# get default team from Beams HR Settings
		default_team = frappe.db.get_single_value('Beams Admin Settings', 'default_hd_ticket_team')

		if default_team:
			self.agent_group = default_team

		if self.ticket_type and not self.agent_group:
			if frappe.db.get_value('HD Ticket Type', self.ticket_type ,'team_name'):
				self.agent_group = frappe.db.get_value('HD Ticket Type', self.ticket_type ,'team_name')

	def after_insert(self):
		'''After insert event of HD Ticket'''

		super().on_update()
		self.send_after_insert_notification()

	def send_after_insert_notification(self):
		if self.agent_group and frappe.db.exists('Notification', { 'enabled':1, 'document_type':'HD Ticket', 'event':'New' }):
			notification = frappe.db.get_value('Notification', { 'enabled':1, 'document_type':'HD Ticket', 'event':'New' } )
			subject_template = frappe.db.get_value('Notification', notification, 'subject') or ''
			message_template = frappe.db.get_value('Notification', notification, 'message') or ''
			subject = frappe.render_template(subject_template, {"doc": self})
			message = frappe.render_template(message_template, {"doc": self})
			# Fetch all L2 users from the team
			hd_team = frappe.get_doc("HD Team", self.agent_group)
			escalation_agent_ids = [row.agent for row in hd_team.escalation_to]
			for email in escalation_agent_ids:
				frappe.get_doc({
					"doctype": "Notification Log",
					"subject": subject,
					"for_user": email,
					"type": "Alert",
					"document_type": "HD Ticket",
					"document_name": self.name,
					"email_content": message
				}).insert(ignore_permissions=True)

	def set_first_responded_on(self):
		'''
			Override set_first_responded_on to prevent updating the field on email reply.
		'''
		return

	# `on_communication_update` is a special method exposed from `Communication` doctype.
	# It is called when a communication is updated. Beware of changes as this effectively
	# is an external dependency. Refer `communication.py` of Frappe framework for more.
	# Since this is called from communication itself, `c` is the communication doc.
	def on_communication_update(self, c):
		# If communication is incoming, then it is a reply from customer, and ticket must
		# be reopened.
		# handle re opening tickets for email
		if c.sent_or_received == "Received":
			# check if agent has replied

			if self.first_responded_on and self.status != "Closed":
				self.status = self.ticket_reopen_status
			else:
				self.status = self.default_open_status
		# If communication is outgoing, it must be a reply from agent
		if c.sent_or_received == "Sent":
			# Set first response date if not set already
			# self.first_responded_on = (
			# 	self.first_responded_on or frappe.utils.now_datetime()
			# )

			# TODO: remove this feature once we add automation feature
			if frappe.db.get_single_value("HD Settings", "auto_update_status"):
				self.status = frappe.db.get_single_value(
					"HD Settings", "update_status_to"
				)

		# Fetch description from communication if not set already. This might not be needed
		# anymore as a communication is created when a ticket is created.
		self.description = self.description or c.content
		# Save the ticket, allowing for hooks to run.
		self.save()

@frappe.whitelist()
def assign_ticket_to_agent(ticket_id, agent):
	"""
		Assign ticket to a specific agent
	"""
	notify = 0
	if agent != frappe.session.user:
		notify = 1
	if not frappe.db.exists('HD Ticket', ticket_id):
		frappe.throw(f'Ticket {ticket_id} does not exist.')

	ticket_doc = frappe.get_doc('HD Ticket', ticket_id)
	ticket_doc.status = 'Working'
	ticket_doc.assigned_agent = agent
	ticket_doc.assigned_agent_name = frappe.db.get_value('User', agent, 'full_name') or ''
	if not ticket_doc.first_responded_on:
		ticket_doc.first_responded_on = now_datetime()
	ticket_doc.save(ignore_permissions=True)

	# Clear previous assignments
	clear_all_assignments('HD Ticket', ticket_id, ignore_permissions=True)

	assign_to_user({
		'doctype': 'HD Ticket',
		'name': ticket_id,
		'assign_to': [agent],
		'description': 'Ticket assigned to you.',
		'notify': notify
	})
	return {"message": f'Ticket {ticket_id} assigned to {agent}.'}

def process_escalation_notifications():
	"""
		Check for overdue Helpdesk tickets and send escalation emails for response or resolution delays.
	"""
	enable_escalation = frappe.db.get_single_value("HD Settings", "enable_escalation_notifications")
	if not enable_escalation:
		return

	response_template = frappe.db.get_single_value("HD Settings", "response_due_template")
	resolution_template = frappe.db.get_single_value("HD Settings", "resolution_due_template")

	now = now_datetime()
	escalation_data = [
		("response_due_escalation_send", "assigned_agent", "response_by", response_template),
		("resolution_due_escalation_send", "resolution_date", "resolution_by", resolution_template)
	]

	for flag, date_field, due_field, template in escalation_data:
		if not template:
			continue
		tickets = frappe.get_all(
			"HD Ticket",
			filters={flag: 0, date_field: ["is", "not set"], due_field: ["<", now]},
			fields=["name", "agent_group"]
		)
		for ticket in tickets:
			ticket_doc = frappe.get_doc("HD Ticket", ticket.name)
			send_escalation_notification(ticket_doc, template)
			frappe.db.set_value("HD Ticket", ticket.name, flag, 1)

def send_escalation_notification(ticket_doc, template_name):
	"""
		Send an escalation email notification to the designated escalation contact for a Helpdesk ticket.
	"""
	if not ticket_doc.agent_group:
		return

	escalation_agent_ids = get_l2_agents_for_team(ticket_doc.agent_group)

	email_template = frappe.get_doc("Email Template", template_name)
	subject = frappe.render_template(email_template.subject or "", {"doc": ticket_doc})
	message = frappe.render_template(email_template.response, {"doc": ticket_doc})

	send_email_notifications(subject, message, escalation_agent_ids, "HD Ticket", ticket_doc.name, send_system_notification=True)

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	if is_admin(user):
		return

	#  To handle the case for normal users i.e. not agents
	customer = get_customer(user)
	query = "(`tabHD Ticket`.owner = {user} OR `tabHD Ticket`.contact = {user} \
	OR `tabHD Ticket`.raised_by = {user} \
	OR `tabHD Ticket`.reports_to_email = {user})".format(
		user=frappe.db.escape(user)
	)
	for c in customer:
		query += " OR `tabHD Ticket`.customer={customer}".format(
			customer=frappe.db.escape(c)
		)

	if not is_agent(user):
		return query

	enable_restrictions = frappe.db.get_single_value(
		"HD Settings", "restrict_tickets_by_agent_group"
	)
	if not enable_restrictions:
		return  # If not enabled, return all tickets

	show_tickets_without_team = frappe.db.get_single_value(
		"HD Settings", "do_not_restrict_tickets_without_an_agent_group"
	)

	teams = get_agents_team()

	if show_tickets_without_team:
		query += " OR (`tabHD Ticket`.agent_group is null OR `tabHD Ticket`.agent_group = '')"

	# If agent belongs to the team which has ignore_permission set to 1.
	# that means this team can see all the tickets without any restriction,
	# Event the other team's tickets.
	if any(team.get("ignore_restrictions") for team in teams):
		all_teams = frappe.get_all("HD Team", pluck="name")
		if not all_teams:
			return query
		all_teams = ", ".join(f"'{team}'" for team in all_teams)
		query += f" OR (`tabHD Ticket`.agent_group in ({all_teams}))".format(
			all_teams=all_teams
		)
		if not show_tickets_without_team:
			query += " OR (`tabHD Ticket`.agent_group is null)"
		return query

	query += (
		" OR (JSON_SEARCH(`tabHD Ticket`._assign, 'all', {user}) IS NOT NULL)".format(
			user=frappe.db.escape(user)
		)
	)

	team_names = [t.get("team_name") for t in teams]

	if not team_names:
		return query

	# Here we will apply the restriction based on the teams the agent belongs to.
	team_names = ", ".join(f"'{team}'" for team in team_names)
	query += f" OR (`tabHD Ticket`.agent_group in ({team_names}))".format(
		team_names=team_names
	)

	return query

def get_agents_team():
	QBTeam = frappe.qb.DocType("HD Team")
	QBTeamMember = frappe.qb.DocType("HD Team Member")
	QBEscalationTo = frappe.qb.DocType("Ticket Agents")

	teams = (
		frappe.qb.from_(QBTeamMember)
		.where(
			(QBTeamMember.user == frappe.session.user)
			| (QBEscalationTo.user == frappe.session.user)
		)
		.join(QBTeam)
		.on(QBTeam.name == QBTeamMember.parent)
		.join(QBEscalationTo)
		.on(QBTeam.name == QBEscalationTo.parent)
		.select(QBTeam.team_name, QBTeam.ignore_restrictions)
		.run(as_dict=True)
	)
	return teams

def has_permission(doc, user=None):
	if not user:
		user = frappe.session.user

	# Direct access for non-agent users based on same fields used in get_permission_query_conditions
	if (
		doc.owner == user
		or doc.contact == user
		or doc.raised_by == user
		or getattr(doc, "reports_to_email", None) == user
		or doc.customer in get_customer(user)
		or is_admin(user)
	):
		return True

	# If user is not an agent, same as query builder: they should not see anything else
	if not is_agent(user):
		return False

	# Agent restriction settings
	enable_restrictions = frappe.db.get_single_value(
		"HD Settings", "restrict_tickets_by_agent_group"
	)
	if not enable_restrictions:
		return True

	show_tickets_without_team = frappe.db.get_single_value(
		"HD Settings", "do_not_restrict_tickets_without_an_agent_group"
	)

	# Same logic: if tickets without a team should be visible
	if show_tickets_without_team and not doc.get("agent_group"):
		return True

	# Assigned tickets (JSON_SEARCH equivalent)
	if doc.get("_assign"):
		try:
			assignees = json.loads(doc._assign)
			if user in assignees:
				return True
		except Exception as e:
			frappe.log_error("Error in Has Permission check of HD Ticket", e)
			return False

	# Agent teams
	teams = get_agents_team()

	# Same logic: team with ignore_restrictions sees all tickets
	if any(team.get("ignore_restrictions") for team in teams):
		return True

	# Collect team names
	team_names = [t.get("team_name") for t in teams]

	# If user is part of team and ticket belongs to that team, allow
	if doc.get("agent_group") in team_names:
		return True

	return False

@frappe.whitelist()
def handle_reason_for_status_change(ticket_id, status, reason):
	"""
		Handle reason for status on ticket
	"""
	valid_statuses = ['Closed', 'Open', 'Hold']

	if not frappe.db.exists('HD Ticket', ticket_id):
		frappe.throw(f'Ticket {ticket_id} does not exist.')

	if status not in valid_statuses:
		frappe.throw(f'Invalid status {status}. Valid statuss are: {", ".join(valid_statuses)}')

	#Using get_doc and save to tigger hooks and other logics
	ticket_doc = frappe.get_doc('HD Ticket', ticket_id)
	ticket_doc.status = status
	if status == 'Closed':
		ticket_doc.resolution_date = frappe.utils.now_datetime()
		ticket_doc.resolution_details = reason
	ticket_doc.save(ignore_permissions=True)

	# Auto assign ticket to session user on Re-Open
	if status == 'Open':
		assign_ticket_to_agent(ticket_id, frappe.session.user)

	# Send on hold notification to L2 agents
	if status == 'Hold' and ticket_doc.agent_group:
		send_on_hold_notification_to_l2(ticket_id, ticket_doc.agent_group, reason)

	# Add comment with reason
	text = _('Changing the Status to {0} with Reason : {1}').format(
		frappe.bold(status),
		frappe.bold(reason)
	)
	ticket_doc.add_comment(comment_type='Comment', text=text)

	return {
		"message": f'Ticket {ticket_id} status updated successfully.'
	}

def send_on_hold_notification_to_l2(ticket_id, team, reason):
	"""
		Send notification to L2 agents when ticket is put on Hold
	"""
	template_name = frappe.db.get_single_value("HD Settings", "on_hold_template")
	escalation_agent_ids = []

	if template_name and frappe.db.exists('HD Ticket', ticket_id) and frappe.db.exists('HD Team', team):
		escalation_agent_ids = get_l2_agents_for_team(team)
		if escalation_agent_ids:
			ticket_doc = frappe.get_doc('HD Ticket', ticket_id)

			email_template = frappe.get_doc("Email Template", template_name)
			subject = frappe.render_template(email_template.subject or "", {"doc": ticket_doc, "reason": reason})
			message = frappe.render_template(email_template.response, {"doc": ticket_doc, "reason": reason})

			send_email_notifications(subject, message, escalation_agent_ids, "HD Ticket", ticket_doc.name, send_system_notification=True)

def get_l2_agents_for_team(hd_team):
	"""
		Get L2 agents for a given HD Team
	"""
	if not frappe.db.exists('HD Team', hd_team):
		return []

	# Fetch all L2 users from the team
	hd_team = frappe.get_doc("HD Team", hd_team)
	escalation_agent_ids = [row.agent for row in hd_team.escalation_to]
	return escalation_agent_ids

def send_email_notifications(subject, message, recipients, doctype, docname, send_system_notification=False):
	"""
		Send email notifications
	"""
	instantly_send_email = frappe.db.get_single_value("HD Settings", "instantly_send_email") or 0

	#Send email notification
	frappe.sendmail(
		recipients = recipients,
		subject = subject,
		message = message,
		reference_doctype = doctype,
		reference_name = docname,
		now = instantly_send_email
	)

	#Send notification log entries
	if send_system_notification:
		for email in recipients:
			# Avoid sending notification to non existing users or self
			if frappe.db.exists('User', email) and frappe.session.user != email:
				frappe.get_doc({
					"doctype": "Notification Log",
					"subject": subject,
					"email_content": message,
					"for_user": email,
					"type": "Alert",
					"document_type": doctype,
					"document_name": docname,
				}).insert(ignore_permissions=True)
