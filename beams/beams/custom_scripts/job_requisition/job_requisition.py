import json

import frappe
from frappe.utils import nowdate
from frappe import ValidationError


def validate_job_requisition(doc, method):
    # Adjusted to use request_for instead of request_type
    if doc.request_for == 'Employee Exit':
        if not doc.employee_left:
            raise ValidationError("Please select at least one employee who has left.")
    else:
        doc.employee_left = []

@frappe.whitelist()
def create_job_opening_from_job_requisition(doc, method):
    '''
    Create a Job Opening when the Job Requisition is approved.

    '''
    if doc.workflow_state == "Approved":
        job_opening = frappe.new_doc('Job Opening')
        job_opening.job_requisition = doc.name
        job_opening.posting_date = frappe.utils.nowdate()
        job_opening.employment_type = doc.employment_type
        job_opening.no_of_days_off = doc.no_of_days_off
        job_opening.designation = doc.designation
        job_opening.min_education_qual = doc.min_education_qual
        job_opening.min_experience = doc.min_experience
        job_opening.expected_compensation = doc.expected_compensation
        job_opening.job_title = doc.job_title
        job_opening.no_of_positions = doc.no_of_positions
        job_opening.employment_type = doc.employment_type
        job_opening.department = doc.department
        job_opening.designation = doc.designation
        job_opening.location = doc.location

        # Validation checks
        if not job_opening.employment_type:
            frappe.throw("Please specify the Employment Type in the Job Requisition.")
        if not job_opening.no_of_days_off:
            frappe.throw("Please specify the Number of Days Off in the Job Requisition.")
        if not job_opening.designation:
            frappe.throw("Please specify the Designation in the Job Requisition.")
        if not job_opening.min_education_qual:
            frappe.throw("Please specify the Minimum Education Qualification in the Job Requisition.")
        if not job_opening.min_experience:
            frappe.throw("Please specify the Minimum Experience in the Job Requisition.")
        if not job_opening.expected_compensation:
            frappe.throw("Please specify the Expected Compensation in the Job Requisition.")
        if not job_opening.no_of_positions:
            frappe.throw("Please specify the Number of Positions in the Job Requisition.")

        for skill in doc.skill_proficiency:
            job_opening.append("skill_proficiency", {
                "skill": skill.skill,
                "proficiency": skill.proficiency
            })

        # Insert and submit the Job Opening document
        job_opening.insert()
        frappe.msgprint(f"Job Opening {job_opening.name} has been created successfully.", alert=True, indicator="green")

@frappe.whitelist()
def on_update(doc, method=None):
    """
    Method triggered after the document is updated.
    It checks if the workflow state has changed to "Cancelled".
    """
    # Fetch the document state before saving
    old_doc = doc.get_doc_before_save()

    # Check if the old workflow state is different from the new one and if the new state is "Cancelled"
    if old_doc and old_doc.workflow_state != doc.workflow_state and doc.workflow_state == "Cancelled":
        job_opening_closed(doc)

@frappe.whitelist()
def job_opening_closed(doc):
    '''
    Close the linked Job Opening when the Job Requisition is cancelled.
    '''
    job_opening = frappe.db.get_value('Job Opening', {'job_requisition': doc.name}, 'name')
    if job_opening:
        job_opening_doc = frappe.get_doc('Job Opening', job_opening)

        # Check if it's already closed to prevent running this again
        if job_opening_doc.status == "Closed":
            frappe.msgprint(f"Job Opening {job_opening_doc.name} is already closed.")
            return

        # Otherwise, proceed to close it
        job_opening_doc.db_set("status", "Closed")
        job_opening_doc.db_set("closed_on", nowdate())
        job_opening_doc.save(ignore_permissions=True)
        frappe.msgprint(f"Job Opening {job_opening_doc.name} has been closed.")
    else:
        frappe.msgprint(f"No Job Opening found for Job Requisition {doc.name}.")


@frappe.whitelist()
def display_template_content(template_name, doc):
    """
    This function fetches the Job Description Template and renders its content dynamically 
    using the details of the Job Requisition document, returning the formatted job description 
    for display.
    """
    
    if isinstance(doc, str):
        doc = frappe.parse_json(doc)  
    
    job_description_template = frappe.get_value("Job Description Template",{'name': template_name},['description'])

    if job_description_template:
        
        rendered_description = frappe.render_template(job_description_template, doc)
        return rendered_description  
    return ""


