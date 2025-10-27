from frappe.desk.form.assign_to import add as assign_to_user
from frappe.desk.form.assign_to import clear as clear_all_assignments
from frappe.utils import now_datetime
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket

import frappe


class HDTicketOverride(HDTicket):

	def on_update(self):
		'''Extend on_update to auto-assign when ticket is Open.'''

		super().on_update()
		if self.agent_group and self.status == 'Open':
			self.handle_assignment_by_team()

	def validate(self):
		'''Extend validate to set agent group automatically.'''

		super().validate()
		self.set_agent_group()

	def handle_assignment_by_team(self):
		'''Assign ticket to all active agents in the selected agent group.'''

		if not self.agent_group:
			return

		if not frappe.db.exists('HD Team', self.agent_group):
			return

		# Fetch all active users from the team
		active_users = self.get_active_users_from_team(self.agent_group)
		if not active_users:
			return

		# Assign to all active agents
		for user in active_users:
			existing_todo = frappe.db.exists('ToDo', {
				'reference_type': self.doctype,
				'reference_name': self.name,
				'owner': user,
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
		else:
			self.agent_group = ''



@frappe.whitelist()
def assign_ticket_to_agent(ticket_name, agent):
    """
    Assign ticket to a specific agent
    """

    if not frappe.db.exists('HD Agent', {'user': agent, 'is_active': 1}):
        frappe.throw(f'User {agent} is not an active HD Agent.')

    if not frappe.db.exists('HD Ticket', ticket_name):
        frappe.throw(f'Ticket {ticket_name} does not exist.')

    todo_exists = frappe.db.exists('ToDo', {
        'reference_type': 'HD Ticket',
        'reference_name': ticket_name,
        'owner': agent,
        'status': ['!=', 'Cancelled'],
    })

    if todo_exists:
        frappe.msgprint(f'Ticket {ticket_name} is already assigned to {agent}.')
        return

    assign_to_user({
        'doctype': 'HD Ticket',
        'name': ticket_name,
        'assign_to': [agent],
        'description': 'Ticket assigned to you.',
    })

    frappe.msgprint(f'Ticket {ticket_name} has been assigned to {agent}.')



@frappe.whitelist()
def assign_to_current_user(docname, doctype):
    """Assign ticket to current user if it's Open or Transferred using Document API"""
    current_user = frappe.session.user

    doc = frappe.get_doc(doctype, docname)

    if doc.status in ['Open', 'Transferred'] and doc.status_category == 'Open':
        clear_all_assignments(doctype, docname, ignore_permissions=True)

        doc.status = 'Replied'
        doc.save(ignore_permissions=True)

    assign_to_user({
        "assign_to": [current_user],
        "doctype": doctype,
        "name": docname,
        "notify": 0
    })

    return {"message": f"Ticket {docname} assigned to {current_user}"}




def process_escalation_notifications():
    """
    	Check for overdue Helpdesk tickets and send escalation emails for response or resolution delays.
    """
    hd_settings = frappe.get_single("HD Settings")
    if not hd_settings.enable_escalation_notifications:
        return

    now = now_datetime()
    escalation_data = [
        ("response_due_escalation_send", "first_responded_on", "response_by", hd_settings.response_due_template, "Response"),
        ("resolution_due_escalation_send", "resolution_date", "resolution_by", hd_settings.resolution_due_template, "Resolution")
    ]

    for flag, date_field, due_field, template, notif_type in escalation_data:
        if not template:
            continue
        tickets = frappe.get_all(
            "HD Ticket",
            filters={flag: 0, date_field: ["is", "not set"], due_field: ["<", now]},
            fields=["name", "agent_group"]
        )
        for ticket in tickets:
            ticket_doc = frappe.get_doc("HD Ticket", ticket.name)
            send_escalation_notification(ticket_doc, template, notif_type)
            frappe.db.set_value("HD Ticket", ticket.name, flag, 1)


def send_escalation_notification(ticket_doc, template_name):
    """
    	Send an escalation email notification to the designated escalation contact for a Helpdesk ticket.
    """
    hd_team = ticket_doc.agent_group
    if not hd_team:
        return

    hd_team_doc = frappe.get_doc("HD Team", hd_team)
    if not hd_team_doc.escalation_to:
        return

    user_email = frappe.db.get_value("Employee", hd_team_doc.escalation_to, "user_id")
    if not user_email:
        return

    email_template = frappe.get_doc("Email Template", template_name)
    subject = frappe.render_template(email_template.subject or "", {"doc": ticket_doc})
    message = frappe.render_template(email_template.response, {"doc": ticket_doc})

    frappe.sendmail(
        recipients=[user_email],
        subject=subject,
        message=message,
        reference_doctype="HD Ticket",
        reference_name=ticket_doc.name
    )
