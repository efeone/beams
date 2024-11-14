# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role
from frappe.model.document import Document


class TrainingRequest(Document):

    def after_insert(self):
        self.create_todo_on_training_request_creation()

    def create_todo_on_training_request_creation(self):
        """
        Create a ToDo for HR Manager when a new Training Request is created or updated.
        """
        # Fetch users with the "HR Manager" role
        users = get_users_with_role("HR Manager")

        if users:
            description = f"New Training Request Created for {self.employee_name}.<br>Please review and update details or take necessary actions."

            # Assign ToDo task to HR Managers
            add_assign({
                "assign_to": users,
                "doctype": "Training Request",  # Dynamically use the doctype of the current document
                "name": self.name,
                "description": description
            })
