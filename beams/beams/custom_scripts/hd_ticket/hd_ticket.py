import frappe
from frappe.desk.form.assign_to import add as assign_to_user
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket

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
