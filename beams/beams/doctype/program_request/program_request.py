# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from frappe.utils import getdate
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

class ProgramRequest(Document):
    def validate(self):
        self.validate_start_date_and_end_dates()

    @frappe.whitelist()
    def validate_start_date_and_end_dates(self):
        """
        Validates that start_date and end_date are properly set and checks
        if start_date is not later than end_date.
        """
        if not self.start_date or not self.end_date:
            return
        # Convert dates to proper date objects
        start_date = getdate(self.start_date)
        end_date = getdate(self.end_date)

        if start_date > end_date:
            frappe.throw(
                msg=_("Start Date cannot be after End Date."),
                title=_("Validation Error")
            )
    def on_update_after_submit(self):
        self.create_project_from_program_request()


    def create_project_from_program_request(self):
        """
        Create a Project from the Program Request if the workflow state is 'Approved',
        and assign it to all users with the "Operations Head" role.
        """

        # Check if the Program Request already has a linked Project
        if self.project:
            frappe.msgprint(_("A Project is already linked to this Program Request: <b>{0}</b>").format(self.project), alert=True)
            return

        # Get current Program Request details
        program_request_id = self.name
        program_request = frappe.get_doc('Program Request', program_request_id)

        doc_before_save = self.get_doc_before_save()

        # Check if the workflow state is 'Approved'
        if not (doc_before_save.workflow_state == "Pending Approval" and program_request.workflow_state == 'Approved'):
            return

        # Check if a Project already exists for this Program Request
        if frappe.db.exists("Project", {"program_request": program_request_id}):
            frappe.msgprint(_("A Project already exists for this Program Request."))
            return

        if frappe.db.exists("Project", {'project_name': program_request.program_name}):
            frappe.msgprint(_("A Project already exists for this Program."))
            return

        # Get all users with the "Operations Head" role
        operation_heads = get_users_with_role("Operations Head")

        # Attempt to create a new Project
        try:
            project = frappe.get_doc({
                'doctype': 'Project',
                'project_name': program_request.program_name,
                'program_request': program_request_id,
                'expected_start_date': program_request.start_date,
                'expected_end_date': program_request.end_date,
            })
            project.insert(ignore_permissions=True)

            self.db_set('project', project.name)
            frappe.msgprint(_("Project <b>{0}</b> has been created successfully.").format(project.project_name),indicator="green",alert=1,)

            # Assign ToDo to all Operation Heads
            for user in operation_heads:
                self.assign_todo_to_user(user, "Project", project.name, f"New Project Created: {self.program_name}")

            return project.name

        except Exception as e:
            frappe.msgprint(_("Error creating project: {0}").format(str(e)))

    def assign_todo_to_user(self, user, doctype_name, doc_name, action_description):
        """Assign a ToDo to a specific user"""
        add_assign({
            "assign_to": [user],  # Assign to individual user
            "doctype": doctype_name,
            "name": doc_name,
            "description": f"New {doctype_name} Created: {doc_name}.<br>{action_description}"
        })
