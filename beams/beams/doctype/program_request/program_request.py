# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form

class ProgramRequest(Document):
    pass

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

    # Send a message to confirm the action
    message = _('Project created successfully! {0}').format(
        frappe.utils.get_link_to_form('Project', project.name)
    )
    frappe.msgprint(message)

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
