import frappe
from frappe.desk.form.assign_to import add as assign_to_user
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket


class HDTicketOverride(HDTicket):

    def on_update(self):
        super().on_update()
        if self.agent_group and self.status == "Open":
            self.handle_assignment_by_team()

    def validate(self):
        super().validate()
        self.set_agent_group()


    def handle_assignment_by_team(self):
        """Auto-assign the ticket to all active agents in the agent group team."""
        try:
            if not self.agent_group:
                return

            team_exists = frappe.db.exists("HD Team", self.agent_group)
            if not team_exists:
                return

            active_users = self.get_active_users_from_team(self.agent_group)
            if not active_users:
                return

            for user in active_users:
                existing_todo = frappe.db.exists("ToDo", {
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                    "owner": user,
                    "status": ["!=", "Cancelled"],
                })

                if not existing_todo:
                    assign_to_user({
                        'doctype': self.doctype,
                        'name': self.name,
                        'assign_to': [user],
                        'description': 'Auto-assigned to active HD Agent from team',
                    })

        except Exception:
            frappe.log_error(frappe.get_traceback(), "handle_assignment_by_team")

    def get_active_users_from_team(self, team_name):
        """Get list of active HD Agents from a given HD Team."""
        try:
            if not team_name or not frappe.db.exists("HD Team", team_name):
                return []

            team = frappe.get_doc("HD Team", team_name)
            users = []

            for row in team.users:
                for user in row.user.split(","):
                    user = user.strip()
                    if frappe.db.exists("HD Agent", {"user": user, "is_active": 1}):
                        users.append(user)

            return users

                                                                                                                     
        except Exception:
            frappe.log_error(frappe.get_traceback(), "get_active_users_from_team")
            return []

    def set_agent_group(self):
        """Set agent_group based on selected ticket_type"""
        if not self.ticket_type:
            self.agent_group = ""
            return

        team_name = frappe.db.get_value("HD Ticket Type", self.ticket_type, "team_name")
        self.agent_group = team_name or ""
