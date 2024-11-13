import frappe
import json
from frappe import _

def get_context(context):
    opening = frappe.form_dict.job_opening
    job_opening = {}
    if frappe.db.exists('Job Opening', opening):
        job_opening = frappe.get_doc('Job Opening', opening)
    else:
        frappe.log_error(str(frappe.form_dict.job_opening), 'Invalid Job Application Link')
        frappe.throw(_("Sorry, the link you were using is not valid."), frappe.PermissionError)
    context.job_opening = job_opening

@frappe.whitelist(allow_guest=True)
def submit_job_application(applicant_name, email_id, phone_number, min_experience=None, min_education_qual=None, job_title=None, location=None, resume_attachment=None, skill_proficiency=None):
	# Create a new Job Applicant document
	job_applicant_doc = frappe.new_doc('Job Applicant')
	job_applicant_doc.applicant_name = applicant_name
	job_applicant_doc.email_id = email_id
	job_applicant_doc.phone_number = phone_number
	job_applicant_doc.min_experience = min_experience
	job_applicant_doc.min_education_qual = min_education_qual
	job_applicant_doc.job_title = job_title
	job_applicant_doc.location = location
	job_applicant_doc.resume_attachment = resume_attachment

	# Process skills if provided
	if skill_proficiency:
		try:
			skills_data = json.loads(skill_proficiency)
			# Append skills to the child table
			for skill_data in skills_data:
				job_applicant_doc.append("skill_proficiency", {
					"skill": skill_data.get("skill"),
					"proficiency": skill_data.get("rating")
				})
		except json.JSONDecodeError:
			frappe.throw("Invalid JSON format for skills data")

	# job_applicant.flags.ignore_mandatory = True
	job_applicant_doc.insert()

	# Return a success message
	return {"message": "Job application submitted successfully"}
