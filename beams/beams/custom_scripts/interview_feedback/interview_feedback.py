import frappe

def on_interview_feedback_creation(doc, method):
    '''
    Update the Job Applicant's status to 'Interview Ongoing' when an Interview Feedback is created.
    '''
    job_applicant_doc = frappe.get_doc("Job Applicant", doc.job_applicant)
    if job_applicant_doc.status != "Interview Ongoing":
        job_applicant_doc.status = "Interview Ongoing"
        job_applicant_doc.save()
