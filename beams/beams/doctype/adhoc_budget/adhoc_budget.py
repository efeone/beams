import frappe
from frappe.desk.form.assign_to import add as add_assign
from frappe.model.document import Document
from frappe.utils.user import get_users_with_role

class AdhocBudget(Document):

    def after_insert(self):
        self.create_todo_on_creation_for_adhoc_budget()

    def on_update(self):
        self.create_todo_on_verified_by_finance()

    def on_update_after_submit(self):
        self.create_todo_on_verified_by_finance()

    def create_todo_on_creation_for_adhoc_budget(self):
        """
        Creates a ToDo task for Accounts Users when a new Adhoc Budget is created.
        Ensures that each Accounts User gets a task to review and update the new budget.
        """
        users = get_users_with_role("Accounts User")
        if users:
            description = f"New Adhoc Budget Created: {self.project}. Please review and update details or take necessary actions."
            for user in users:
                if not frappe.db.exists('ToDo', {'reference_name': self.name, 'assign_to': user}):
                    add_assign({
                        "assign_to": [user],
                        "doctype": "Adhoc Budget",
                        "name": self.name,
                        "description": description
                    })

    def create_todo_on_verified_by_finance(self):
        """
        Creates a ToDo task for the CEO based on the workflow state of the Adhoc Budget.
        - If the state is "Verified By Finance", creates a task for the CEO to proceed with the next step.
        - If the state is "Rejected By Finance", creates a task for the CEO to review and revise or proceed with feedback.
        """
        if self.workflow_state == "Verified By Finance":
            ceo_users = get_users_with_role("CEO")
            if ceo_users:
                description = f"Approved by Finance: Adhoc Budget {self.project}. Please proceed with the next step."
                if not frappe.db.exists('ToDo', {'reference_name': self.name, 'reference_type': 'Adhoc Budget', 'description':description}):
                    add_assign({
                        "assign_to": ceo_users,
                        "doctype": "Adhoc Budget",
                        "name": self.name,
                        "description": description
                    })
        elif self.workflow_state == "Rejected By Finance":
            ceo_users = get_users_with_role("CEO")
            if ceo_users:
                description = f"Rejected by Finance: Adhoc Budget {self.project}. Please review and revise, or proceed with their feedback."
                if not frappe.db.exists('ToDo', {'reference_name': self.name, 'reference_type': 'Adhoc Budget', 'description':description}):
                    add_assign({
                        "assign_to": ceo_users,
                        "doctype": "Adhoc Budget",
                        "name": self.name,
                        "description": description
                    })
