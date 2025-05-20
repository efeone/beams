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

    def handle_assignment_by_team(self):
        """Auto-assign to an agent based on the team's assignment rule."""
        try:
            if not self.agent_group:
                return

            team_exists = frappe.db.exists("HD Team", self.agent_group)
            if not team_exists:
                return

            team = frappe.get_doc("HD Team", self.agent_group)

            if not team.assignment_rule:
                return

            rule_exists = frappe.db.exists("Assignment Rule", team.assignment_rule)
            if not rule_exists:
                return

            rule = frappe.get_doc("Assignment Rule", team.assignment_rule)

            active_users = self.get_active_users_from_team(self.agent_group)
            if not active_users:
                return

            selected_user = self.select_user_from_assignment_rule(rule, active_users)
            if not selected_user:
                return

            existing_todo = frappe.db.exists("ToDo", {
                "reference_type": self.doctype,
                "reference_name": self.name,
                "owner": selected_user,
                "status": ["!=", "Cancelled"],
            })

            if not existing_todo:
                assign_to_user({
                    'doctype': self.doctype,
                    'name': self.name,
                    'assign_to': [selected_user],
                    'description': 'Auto-assigned to active HD Agent from team',
                })

        except Exception:
            frappe.log_error(frappe.get_traceback(), "handle_assignment_by_team")


    def get_active_users_from_team(self, team_name):
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

    def select_user_from_assignment_rule(self, rule_doc, active_users):
        eligible_users = [
            u.user for u in rule_doc.users
            if u.user.lower().strip() in [a.lower().strip() for a in active_users]
        ]
        if not eligible_users:
            return None

        if rule_doc.assignment_based_on == "Round Robin":
            return self.get_next_round_robin_user(rule_doc, eligible_users)
        elif rule_doc.assignment_based_on == "Load":
            return self.get_least_assigned_user(eligible_users)

        return eligible_users[0]

    def get_next_round_robin_user(self, rule_doc, eligible_users):
        last_user = rule_doc.get("last_user") or ""
        try:
            idx = eligible_users.index(last_user)
            next_user = eligible_users[(idx + 1) % len(eligible_users)]
        except ValueError:
            next_user = eligible_users[0]
        rule_doc.last_user = next_user
        rule_doc.save(ignore_permissions=True)
        return next_user

    def get_least_assigned_user(self, eligible_users):
        if not eligible_users:
            return None

        counts = frappe.db.sql("""
            SELECT owner, COUNT(*) AS count
            FROM `tabToDo`
            WHERE reference_type = 'HD Ticket'
              AND owner IN %(users)s
              AND status = 'Open'
            GROUP BY owner
        """, {"users": tuple(eligible_users)}, as_dict=True)

        load_map = {user: 0 for user in eligible_users}
        for row in counts:
            load_map[row.owner] = row.count

        return min(load_map, key=load_map.get)

    def get_assigned_agent(self):
        assignees = frappe.parse_json(getattr(self, '_assign', '[]') or '[]')
        if assignees:
            user = assignees[0]
            if frappe.db.exists("HD Agent", {"user": user}):
                return frappe.get_doc("HD Agent", {"user": user})

        todos = frappe.get_all("ToDo", {
            "reference_type": self.doctype,
            "reference_name": self.name,
            "status": "Open"
        }, ["owner"], limit=1)

        if todos:
            user = todos[0].owner
            if frappe.db.exists("HD Agent", {"user": user}):
                return frappe.get_doc("HD Agent", {"user": user})

        return None
