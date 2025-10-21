import frappe
from helpdesk.helpdesk.doctype.hd_team.hd_team import HDTeam


class HDTeamOverride(HDTeam):
    def before_save(self):
        self.set_users_from_agent()

    def set_users_from_agent(self):
        """
        Set users from HD Agent MultiSelect.
        Only active agents are considered.
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
