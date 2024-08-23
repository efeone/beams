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

    def on_submit(self):
        if self.workflow_state == 'Approved':
            self.create_budget_from_adhoc_budget()

    def create_budget_from_adhoc_budget(self):
        """
        Budget Creation On The Approval Of the Adhoc Budget
        """
        budget = frappe.new_doc('Budget')
        budget.budget_against = 'Project'
        budget.project = self.project
        budget.fiscal_year = self.fiscal_year

        budget.applicable_on_material_request = 1
        budget.applicable_on_booking_actual_expenses = 1
        budget.applicable_on_purchase_order = 1

        budget.action_if_annual_budget_exceeded_on_mr = 'Warn'
        budget.action_if_accumulated_monthly_budget_exceeded_on_mr = 'Warn'
        budget.action_if_annual_budget_exceeded_on_po = 'Warn'
        budget.action_if_accumulated_monthly_budget_exceeded_on_po = 'Warn'
        budget.action_if_annual_budget_exceeded = 'Warn'
        budget.action_if_accumulated_monthly_budget_exceeded = 'Warn'

        budget.flags.ignore_validate = True
        budget.flags.ignore_mandatory = True
        budget.flags.ignore_permissions = True

        account_budget_map = {}

        for expense in self.budget_expense:
            account = 'Cost of Goods Sold - E'

            if account in account_budget_map:
                account_budget_map[account] += expense.budget_amount
            else:
                account_budget_map[account] = expense.budget_amount

        for account, total_budget_amount in account_budget_map.items():
            budget.append('accounts', {
                'account': account,
                'budget_amount': total_budget_amount
            })

        budget.insert()
        budget.submit()
