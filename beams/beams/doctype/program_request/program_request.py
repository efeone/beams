# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from frappe.utils import getdate

class ProgramRequest(Document):
    def validate(self):
        self.validate_start_date_and_end_dates()
        self.check_expected_revenue()

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
    @frappe.whitelist()
    def check_expected_revenue(self):
        '''Function to check if Expected Revenue is > 0 when Generates Revenue is checked'''
        if self.generates_revenue and self.expected_revenue <= 0:
            frappe.throw(_("Expected Revenue must be greater than 0."))

    def on_update_after_submit(self):
        self.create_project_from_program_request()

    def create_project_from_program_request(self):
        """
        Create a Project from the Program Request if the workflow state is 'Approved'.
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
        if frappe.db.exists("Project", {"program": program_request_id}):
            frappe.msgprint(_("A Project already exists for this Program Request."))
            return

        if frappe.db.exists("Project", {'project_name': program_request.program_name}):
            frappe.msgprint(_("A Project already exists for this Program."))
            return

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

            return project.name

        except Exception as e:
            frappe.msgprint(_("Error creating project: {0}").format(str(e)))
