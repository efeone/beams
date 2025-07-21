import datetime
import json

import frappe
from frappe import _
from frappe.utils import escape_html
from frappe.utils.file_manager import save_file
from frappe.utils.password import decrypt


def get_context(context):
    '''
        Initializes the context with job applicant details if the applicant ID is valid.
        args:
            context (dict)
        Return : None
    '''
    context.no_cache = 1
    context.doc = {  }
    encrypted_applicant_id = frappe.form_dict.applicant_id
    applicant_id = authorize_applicant_id(encrypted_applicant_id)
    if frappe.db.exists('Job Applicant', applicant_id):
        context.doc = frappe.get_doc('Job Applicant', applicant_id)
    context.languages = frappe.db.get_all('Language', fields=['language_name', 'name'])
    context.license_types = frappe.db.get_all('License Type', fields=['license_type', 'name'])

def authorize_applicant_id(encrypted_applicant_id):
	'''
		Method is used to check the magic link exist or expired
		args:
			encrypted_applicant_id: encrypted value of Applicant ID
		return Applicant ID (example: 123)
	'''
	# Set decrypted_applicant_id as false to initialize
	decrypted_applicant_id = False
	try:
		decrypted_applicant_id = decrypt(encrypted_applicant_id)
	except Exception:
		frappe.log_error(str(encrypted_applicant_id), 'Dirty Applicant Link')
		frappe.throw(_("Sorry, we were not able to decrypt the applicant link"), frappe.PermissionError)

	if decrypted_applicant_id:
		if not frappe.db.exists('Job Applicant', decrypted_applicant_id):
			frappe.log_error(str(decrypted_applicant_id), 'Job Applicant Not exist')
			frappe.throw(_("Sorry, couldn't find any matching Job Applicant"), frappe.PermissionError)
		else:
			is_form_submitted = frappe.db.get_value('Job Applicant', decrypted_applicant_id, 'is_form_submitted')
			if is_form_submitted:
				frappe.log_error(str(decrypted_applicant_id), 'Form Already Submitted')
				frappe.throw(_("Sorry, Form is already Submitted"), frappe.PermissionError)
			else:
				return decrypted_applicant_id

@frappe.whitelist(allow_guest=True)
def update_register_form(docname, data):
    '''
        Updates a Job Applicant document with form data, handling various sections and child tables.
        args:
            docname (str), data (str)
    '''
    try:
        data = json.loads(data)
        print(f"[DEBUG] pdating Job Applicant: {docname} with data: {data}", "Job Application Update")
        if not data.get("applicant_name"):
            frappe.throw("Missing required fields: Applicant Name")
        if frappe.db.exists('Job Applicant', docname):
            doc = frappe.get_doc('Job Applicant', docname)
            for field, value in data.items():
                if field in ["date_of_birth", "interviewed_date"] and value:
                    converted_date = datetime.datetime.strptime(value, "%d-%m-%Y").strftime("%Y-%m-%d")
                    setattr(doc, field, converted_date)
                else:
                    setattr(doc, field, escape_html(value))
            doc.in_india = bool(data.get("in_india"))
            doc.abroad = bool(data.get("abroad"))
            doc.is_form_submitted = bool(data.get("is_form_submitted"))
            doc.travel_required = bool(data.get("travel_required"))
            doc.driving_license_needed = bool(data.get("driving_license_needed"))
            doc.is_work_shift_needed = bool(data.get("is_work_shift_needed"))
            doc.license_type = data.get("license_type", "")

			# Upload payslip documents
            for field in ["payslip_month_1", "payslip_month_2", "payslip_month_3"]:
                if data.get(field):
                    filename = update_file(data[field], 'Job Applicant', docname) or ''
                    setattr(doc, field, filename)
                    
            doc.education_qualification = []
            doc.professional_certification = []
            doc.prev_emp_his = []
            doc.language_proficiency = []
            for row in data.get("educational_qualification", []):
                if row.get('name_of_course_university'):
                    filename = update_file(row.get('attachments'), 'Job Applicant', docname) or ''
                    doc.append("education_qualification", {
						"name_of_course_university": row.get('name_of_course_university'),
						"name_location_of_institution": row.get('name_location_of_institution'),
						"dates_attended_from": int(row.get('dates_attended_from')),
						"dates_attended_to": int(row.get('dates_attended_to')),
						"result": float(row.get('result')),
						"attachments": filename
					})
            for row in data.get("professional_certification", []):
                if row.get("course"):
                    filename = update_file(row.get('attachments'), 'Job Applicant', docname) or ''
                    doc.append("professional_certification", {
						"course": row.get("course"),
						"institute_name": row.get("institute_name"),
						"dates_attended_from": int(row.get("dates_attended_from")),
						"dates_attended_to": int(row.get("dates_attended_to")),
						"type_of_certification": row.get("type_of_certification"),
						"subject_major": row.get("subject_major"),
						"attachments": filename
					})
            for row in data.get("prev_emp_his", []):
                if row.get("name_of_org"):
                    filename = update_file(row.get('attachments'), 'Job Applicant', docname) or ''
                    doc.append("prev_emp_his", {
						"name_of_org": row.get("name_of_org"),
						"prev_designation": row.get("prev_designation"),
						"last_salary_drawn": float(row.get("last_salary_drawn")),
						"name_of_manager": row.get("name_of_manager"),
						"period_of_employment": float(row.get("period_of_employment")),
						"reason_for_leaving": row.get("reason_for_leaving"),
						"attachments": filename
					})
            for row in data.get("language_proficiency", []):
                doc.append("language_proficiency", {
					"language": row["language"],
					"speak": row["speak"],
					"read": row["read"],
					"write": row["write"]
				})
            doc.save(ignore_permissions=True)
            frappe.msgprint(f"{doc.name} updated successfully.", indicator="green", alert=True)
            return {"message": "success", "docname": doc.name}
        else:
            frappe.throw(f"No document found for applicant: {docname}")
    except Exception as e:
            frappe.log_error(
			 title="Job Application Update Failed",
			 message=f"Error updating applicant '{docname}' with data: {data}\nException: {str(e)}")
            return {"message": str(e)}

@frappe.whitelist(allow_guest=True)
def update_file(filedata, doctype, docname):
	'''
		Uploads files to the specified Job Applicant document.
		Args:
			filedata (dict), doctype (str), docname (str)
	'''
	file_name = None
	if filedata and doctype and docname:
		filedata_list = filedata["files_data"]
		if frappe.db.exists(doctype, docname):
			for filedata_item in filedata_list:
				filedoc = save_file(filedata_item["filename"], filedata_item["dataurl"], doctype, docname, decode=True, is_private=0)
				file_name = filedoc.file_url
		else:
			for filedata_item in filedata_list:
				filedoc = save_file(filedata_item["filename"], filedata_item["dataurl"], decode=True, is_private=0)
				file_name = filedoc.file_url
	frappe.db.commit()
	return file_name