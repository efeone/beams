import frappe
from frappe import _
from beams.www.job_portal.index import get_job_applicant_count, get_salary_range

def get_context(context):
	job_opening = frappe.form_dict.job_opening or ''
	if not frappe.db.exists('Job Opening', job_opening):
		frappe.log_error(str(job_opening), 'Job Opening {0} not found')
		frappe.throw(_("Sorry, the link you are following is broken."), frappe.PermissionError)
	context.job = frappe.get_doc('Job Opening', job_opening)
	context.salary_range = get_salary_range(job_opening)
	context.no_of_applications = get_job_applicant_count(job_opening)
	context.education_qualification = ''
	return {
		"context": context
	}