import frappe
@frappe.whitelist()
def create_job_opening_from_job_requisition(doc, method):
    '''
        Creation of Job Opening on the Approval of the Job Requisition.
    '''
    if doc.workflow_state == "Approved":
        job_opening = frappe.new_doc('Job Opening')
        job_opening.job_requisition = doc.name
        job_opening.posting_date = frappe.utils.nowdate()
        job_opening.employment_type = doc.employment_type
        job_opening.no_of_days_off = doc.no_of_days_off
        job_opening.designation = doc.designation
        job_opening.min_education_qual = doc.min_education_qual
        job_opening.min_experience= doc.min_experience
        job_opening.expected_compensation = doc.expected_compensation
        job_opening.job_title = doc.designation
        job_opening.no_of_positions = doc.no_of_positions

        if not job_opening.employment_type:
            frappe.throw("Please specify the Employment Type in the Job Requisition.")
        if not job_opening.no_of_days_off :
            frappe.throw("Please specify the Number of Days Off in the Job Requisition.")
        if not job_opening.designation :
            frappe.throw("Please specify the Designation in the Job Requisition.")
        if not job_opening.min_education_qual:
            frappe.throw("Please specify the Minimum Education Qualification in the Job Requisition.")
        if not job_opening.min_education_qual:
            frappe.throw("Please specify the Minimum Experience in the Job Requisition.")
        if not job_opening.expected_compensation:
            frappe.throw("Please specify the Expected Compensation in the Job Requisition.")
        if not job_opening.no_of_positions:
            frappe.throw("Please specify the Number of Position in the Job Requisition.")

        job_opening.insert()
        job_opening.submit()
        frappe.msgprint(f"Job Opening {job_opening.name} has been created successfully.", alert=True, indicator="green")
