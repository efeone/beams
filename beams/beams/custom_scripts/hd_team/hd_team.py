import frappe
from frappe import _
from helpdesk.helpdesk.doctype.hd_team.hd_team import HDTeam

class HDTeamOverride(HDTeam):
	def before_save(self):
		self.set_users_from_agent()

	def set_users_from_agent(self):
		"""
			Set users from HD Agent MultiSelect. Only active agents are considered.
		"""
		self.users = []

		if not self.agents:
			return

		agent_names = [agent.agent for agent in self.agents]

		active_users = frappe.get_all(
			"HD Agent",
			filters={"name": ["in", agent_names]},
			pluck="user"
		)

		for user in active_users:
			self.append("users", {"user": user})

	def update_assignment_rule_users(self, user, assignment_rule_doc, action="add"):
		if user[0] != "users":
			return
		_user = user[1].get("user")
		if not user:
			frappe.throw(_("User Not found"))
			return

		if action == "add":
			assignment_rule_doc.append("users", {"user": _user})
			if assignment_rule_doc.disabled:
				assignment_rule_doc.disabled = False
			assignment_rule_doc.save()

			# remove the user from the base assignment rule
			base_assignment_rule = frappe.get_value(
				"HD Settings", "HD Settings", "base_support_rotation"
			)
			base_assignment_rule = frappe.get_doc(
				"Assignment Rule", base_assignment_rule
			)
			user_id = frappe.get_value(
				"Assignment Rule User",
				{"user": _user, "parent": base_assignment_rule.name},
			)
			if user_id:
				frappe.delete_doc("Assignment Rule User", user_id)
		else:
			user_id = frappe.get_value(
				"Assignment Rule User",
				{"user": _user, "parent": assignment_rule_doc.name},
			)
			if not user_id:
				return
			frappe.delete_doc("Assignment Rule User", user_id)

			# disable the assignment rule if there are no users
			total_users_in_assignment_rule = frappe.db.count(
				"Assignment Rule User", {"parent": assignment_rule_doc.name}
			)
			if total_users_in_assignment_rule == 0:
				assignment_rule_doc.disabled = True
				assignment_rule_doc.save()


def disable_hd_team_assignment_rule_if_enabled(doc, method):
	"""
		Disable the assignment rule linked to the HD Team if it is enabled.
	"""
	if doc.assignment_rule:
		is_disabled = frappe.get_value("Assignment Rule", doc.assignment_rule, "disabled")
		if not is_disabled:
			frappe.db.set_value("Assignment Rule", doc.assignment_rule, "disabled", 1)
