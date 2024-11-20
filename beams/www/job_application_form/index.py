import frappe
import json
from frappe import _
from frappe.utils.file_manager import save_file

def get_context(context):
	opening = frappe.form_dict.job_opening
	job_opening = {}
	if frappe.db.exists('Job Opening', opening):
		job_opening = frappe.get_doc('Job Opening', opening)
	else:
		frappe.log_error(str(frappe.form_dict.job_opening), 'Invalid Job Application Link')
		frappe.throw(_("Sorry, the link you were using is not valid."), frappe.PermissionError)
	context.job_opening = job_opening
	context.skills = get_skills_from_opening(opening)

@frappe.whitelist(allow_guest=True)
def create_job_applicant(applicant_name, email_id, phone_number, min_experience=None, min_education_qual=None, job_title=None, location=None, resume_attachment=None, skill_proficiency=None):
	'''
		Method to create Job Applicant
	'''
	job_applicant_doc = frappe.new_doc('Job Applicant')
	job_applicant_doc.applicant_name = applicant_name
	job_applicant_doc.email_id = email_id
	job_applicant_doc.phone_number = phone_number
	job_applicant_doc.min_experience = min_experience
	job_applicant_doc.min_education_qual = min_education_qual
	job_applicant_doc.job_title = job_title
	job_applicant_doc.location = location

	# Process skills if provided
	if skill_proficiency:
		try:
			skills_data = json.loads(skill_proficiency)
			for skill_data in skills_data:
				job_applicant_doc.append("skill_proficiency", {
					"skill": skill_data.get("skill"),
					"proficiency": skill_data.get("rating")
				})
		except:
			pass

	job_applicant_doc.flags.ignore_mandatory = True
	job_applicant_doc.save(ignore_permissions=True)
	filename = upload_file(resume_attachment, job_applicant_doc.doctype, job_applicant_doc.name, 'resume_attachment')
	frappe.db.set_value(job_applicant_doc.doctype, job_applicant_doc.name, 'resume_attachment', filename)
	return 1

@frappe.whitelist(allow_guest=True)
def upload_file(filedata, doctype, docname, docfield):
	'''
		Uploads files to the specified Job Applicant document.
		Args:
			filedata (dict), doctype (str), docname (str)
	'''
	file_name = None
	if filedata and doctype and docname:
		filedata = json.loads(filedata)
		filedata_list = filedata["files_data"]
		if frappe.db.exists(doctype, docname):
			for filedata_item in filedata_list:
				filedoc = save_file(filedata_item["filename"], filedata_item["dataurl"], doctype, docname, decode=True, is_private=0, df=docfield)
				file_name = filedoc.file_url
		else:
			for filedata_item in filedata_list:
				filedoc = save_file(filedata_item["filename"], filedata_item["dataurl"], decode=True, is_private=0)
				file_name = filedoc.file_url
	frappe.db.commit()
	return file_name

@frappe.whitelist()
def get_skills_from_opening(job_opening):
	'''
        Method to get Skills from Job Opening
	'''
	skills = []
	if frappe.db.exists('Job Opening', job_opening):
		skills = frappe.db.get_all('Skill Proficiency', { 'parent':job_opening }, 'skill')
	return skills