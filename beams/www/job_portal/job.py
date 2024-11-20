import frappe
from frappe import _
from beams.www.job_portal.index import get_job_applicant_count, get_salary_range

def get_context(context):
	job_opening = frappe.form_dict.job_opening or ''
	if not frappe.db.exists('Job Opening', job_opening):
		frappe.log_error(str(job_opening), 'Job Opening {0} not found')
		frappe.throw(_("Sorry, the link you are following is broken."), frappe.PermissionError)
	opening_doc = frappe.get_doc('Job Opening', job_opening)
	context.job = opening_doc
	context.salary_range = get_salary_range(job_opening)
	context.no_of_applications = get_job_applicant_count(job_opening)

    #Preparing coma seperated string for Prefered qualifications
	qualifications = ''
	for qualification in opening_doc.min_education_qual:
		qualifications += '{}, '.format(qualification.qualification)

    #Removing last 2 chars from the string. which is ',' for the last added qualification
	if qualifications:
		qualifications = qualifications[:-2]
	context.educational_qualifications = qualifications
	return {
		"context": context
	}