# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from frappe.utils import getdate
from frappe import _

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

@frappe.whitelist()
def create_project_from_program_request(program_request_id):
    '''
    Create a Project from the Program Request.
    '''
    # Fetch the Program Request document
    program_request = frappe.get_doc('Program Request', program_request_id)

    # Check if a Project already exists
    if frappe.db.exists("Project", {"program": program_request_id}):
        frappe.throw(_("A Project is already linked to this Program Request."))

    # Create a new Project document
    project = frappe.get_doc({
        'doctype': 'Project',
        'project_name': program_request.program_name,
        'program': program_request.name,
        'expected_start_date': program_request.start_date,
        'expected_end_date': program_request.end_date
    })
    project.insert(ignore_permissions=True)  # Insert the new Project

    # Return the name of the created Project
    return project.name

@frappe.whitelist()
def check_project_exists(program_request_id):
    '''
    Check if a Project exists for the given Program Request.
    '''
    program_request = frappe.get_doc('Program Request', program_request_id)
    program_name = program_request.program_name

    return frappe.db.exists("Project", {"project_name": program_name})
