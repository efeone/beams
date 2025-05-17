import frappe
from frappe.desk.form.assign_to import add as assign_to_user
from frappe.desk.form.assign_to import clear as clear_all_assignments
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket


class HDTicketOverride(HDTicket):

    def on_update(self):
        super(HDTicketOverride, self).on_update()
        self.remove_assignment_if_not_in_team()

    def after_insert(self):
        super(HDTicketOverride, self).after_insert()

    def validate(self):
        super(HDTicketOverride, self).validate()

    def get_active_users_from_team(self, team_name):
        active_users = []
        team_doc = frappe.get_doc("HD Team", team_name)
        for user_entry in team_doc.users:
            agent = frappe.get_value("HD Agent", {"user": user_entry.user, "is_active": 1})
            if agent:
                active_users.append(user_entry.user)
        return active_users

    def remove_assignment_if_not_in_team(self):
        if self.has_value_changed("agent_group") and self.agent_group and self.status == "Open":
            current_assigned_agent_doc = self.get_assigned_agent()

            team_doc = frappe.get_doc("HD Team", self.agent_group)
            assignment_rule = frappe.get_doc("Assignment Rule", team_doc.assignment_rule)

            if (
                current_assigned_agent_doc
                and not current_assigned_agent_doc.in_group(self.agent_group)
            ) and assignment_rule.users:
                clear_all_assignments("HD Ticket", self.name)
                frappe.publish_realtime(
                    "helpdesk:update-ticket-assignee",
                    {"ticket_id": self.name},
                    after_commit=True,
                )

            active_users = self.get_active_users_from_team(self.agent_group)
            if active_users:
                for user in active_users:
                    assign_to_user({
                        'doctype': self.doctype,
                        'name': self.name,
                        'assign_to': [user],
                        'description': 'Auto-assigned to active HD Agent from team',
                    })
         