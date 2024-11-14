import json
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import nowdate, get_url_to_form

@frappe.whitelist()
def create_job_opening_from_job_requisition(doc, method):
    '''
        Create a Job Opening when the Job Requisition is approved.
    '''
    if doc.workflow_state == 'Approved':
        if not frappe.db.exists('Job Opening', { 'job_requisition':doc.name }):
            job_opening = frappe.new_doc('Job Opening')
            job_opening.job_requisition = doc.name
            job_opening.posting_date = nowdate()
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

            for skill in doc.skill_proficiency:
                job_opening.append('skill_proficiency', {
                    "skill": skill.skill,
                    "proficiency": skill.proficiency
                })

            # Insert and submit the Job Opening document
            job_opening.insert()
            frappe.msgprint(
                'Journal Entry Created: <a href="{0}">{1}</a>'.format(get_url_to_form(job_opening.doctype, job_opening.name), job_opening.name),
                alert=True, indicator='green')

@frappe.whitelist()
def on_update(doc, method=None):
    '''
        Method triggered after the document is updated.
        It checks if the workflow state has changed to "Cancelled".
    '''
    # Fetch the document state before saving
    old_doc = doc.get_doc_before_save()

    # Check if the old workflow state is different from the new one and if the new state is "Cancelled"
    if old_doc and old_doc.workflow_state != doc.workflow_state and doc.workflow_state == 'Cancelled':
        close_job_openings(doc)

@frappe.whitelist()
def close_job_openings(doc):
    '''
        Close the linked Job Opening when the Job Requisition is cancelled.
    '''
    job_openings = frappe.db.get_all('Job Opening', {'job_requisition': doc.name, 'status':['!=', 'Closed'] })
    for job_opening in job_openings:
        frappe.db.set_value('Job Opening', job_opening.name, 'status', 'Closed')
        frappe.db.set_value('Job Opening', job_opening.name, 'closed_on',  nowdate())
        frappe.msgprint('Job Opening {0} has been closed'.format(job_opening.name), alert=True, indicator='green')

@frappe.whitelist()
def get_template_content(template_name, doc):
    '''
        This function fetches the Job Description Template and renders its content dynamically
        using the details of the Job Requisition document, returning the formatted job description
        for display.
    '''
    rendered_description = ''
    if frappe.db.exists('Job Description Template', template_name):
        if isinstance(doc, str):
            doc = frappe.parse_json(doc)
        description = frappe.db.get_value('Job Description Template', template_name, 'description')
        if description:
            rendered_description = frappe.render_template(description, doc)
    return rendered_description