import frappe
from frappe.utils import nowdate

@frappe.whitelist()
def create_job_opening_from_job_requisition(doc, method):
    '''
    Create a Job Opening when the Job Requisition is approved.

    '''
    if doc.workflow_state == "Pending Approval":
        department = frappe.get_doc('Department', doc.department)
        head_of_department = department.head_of_department
        if not head_of_department:
            frappe.throw(f"Head of Department is not set for the {doc.department} department.")
        head_of_department_doc = frappe.get_doc('Employee', head_of_department)
        user_email = head_of_department_doc.user_id
        if frappe.session.user != user_email:
            frappe.throw(f"Only the Head of Department ({head_of_department}) can change the workflow state from '<b>Draft</b>' to '<b>Submit for Approval</b>' .")

    if doc.workflow_state == "Approved":
        if not "CEO" in frappe.get_roles(frappe.session.user):
            frappe.throw("Only a user with the 'CEO' role can approve this Job Requisition.")

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
        job_opening.description = doc.description


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
        if not job_opening.description:
            frappe.throw("Please specify the Description in the job Requisition")

        # Insert the Job Opening document
        job_opening.insert()
        frappe.msgprint(f"Job Opening {job_opening.name} has been created successfully.", alert=True, indicator="green")


def on_workflow_cancel(doc, method):
    '''
    Close the linked Job Opening when the Job Requisition is cancelled.

    '''
    # Find the Job Opening linked to this Job Requisition
    job_opening = frappe.db.get_value('Job Opening', {'job_requisition': doc.name}, 'name')

    if job_opening:
        frappe.msgprint(f"Linked Job Opening found: {job_opening}")

        # Fetch the Job Opening document
        job_opening_doc = frappe.get_doc('Job Opening', job_opening)

        # Update the status of the Job Opening to "Closed"
        job_opening_doc.db_set("status", "Closed")

        # Set the closed_on field to the current date
        job_opening_doc.closed_on = nowdate()

        # Cancel the Job Opening
        job_opening_doc.cancel()

        # Ignore validation during cancellation
        job_opening_doc.ignore_validate = True

        # Inform the user
        frappe.msgprint(f"Job Opening {job_opening_doc.name} has been closed.")
    else:
        frappe.msgprint(f"No Job Opening found for Job Requisition {doc.name}.")
