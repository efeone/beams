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
	context.doc = {}
	encrypted_applicant_id = frappe.form_dict.applicant_id
	applicant_id = authorize_applicant_id(encrypted_applicant_id)
	if frappe.db.exists('Job Applicant', applicant_id):
		context.doc = frappe.get_doc('Job Applicant', applicant_id)
	context.languages = frappe.db.get_all('Language', fields=['language_name', 'name'])

def authorize_applicant_id(encrypted_applicant_id):
	'''
		Method is used to check the magic link exist or expired
		args:
			encrypted_applicant_id: encrypted value of Applicant ID
		return Applicant ID (example: 123)
	'''
	decrypted_applicant_id = False
	try:
		decrypted_applicant_id = decrypt(encrypted_applicant_id)
	except Exception:
		frappe.log_error(str(encrypted_applicant_id), 'Dirty Applicant Link')
		frappe.throw(_('Sorry, we were not able to decrypt the applicant link'), frappe.PermissionError)

	if decrypted_applicant_id:
		if not frappe.db.exists('Job Applicant', decrypted_applicant_id):
			frappe.log_error(str(decrypted_applicant_id), 'Job Applicant Not exist')
			frappe.throw(_('Sorry, couldn\'t find any matching Job Applicant'), frappe.PermissionError)
		else:
			is_form_submitted = frappe.db.get_value('Job Applicant', decrypted_applicant_id, 'is_form_submitted')
			if is_form_submitted:
				frappe.log_error(str(decrypted_applicant_id), 'Form Already Submitted')
				frappe.throw(_('Sorry, Form is already Submitted'), frappe.PermissionError)
			else:
				return decrypted_applicant_id

@frappe.whitelist(allow_guest=True)
def update_register_form(docname, form_data=None):
	'''
		Updates a Job Applicant document with form data, handling various sections and child tables.
	'''
	
	try:
		form_data_str = frappe.form_dict.form_data
		form_data = json.loads(form_data_str)

		docname = form_data.get('docname')
		if not docname:
			return {'status': 'error', 'message': 'No document name provided.'}

		if not form_data.get('applicant_name'):
			frappe.throw('Missing required field: Applicant Name')

		doc = frappe.get_doc('Job Applicant', docname)

		def sanitize(field):
			return escape_html(form_data.get(field) or '')

		def convert_date(date_str):
			return datetime.datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d') if date_str else None

		doc.applicant_name = sanitize('applicant_name')
		doc.father_name = sanitize('father_name')
		doc.date_of_birth = convert_date(form_data.get('date_of_birth'))
		doc.gender = sanitize('gender')
		doc.country = sanitize('country')
		doc.marital_status = sanitize('marital_status')
		doc.aadhar_number = sanitize('aadhaar_number_input')

		doc.house_no_name = sanitize('current_house_no')
		doc.street_road = sanitize('current_street')
		doc.locality_village = sanitize('current_locality')
		doc.city = sanitize('current_city')
		doc.district = sanitize('current_district')
		doc.state = sanitize('current_state')
		doc.post_office = sanitize('current_perm_post_office')
		doc.pin_code = sanitize('current_pin')

		doc.phouse_no_name = sanitize('permanent_house_no')
		doc.pstreet_road = sanitize('permanent_street')
		doc.plocality_village = sanitize('permanent_locality')
		doc.pcity = sanitize('permanent_city')
		doc.pdistrict = sanitize('permanent_district')
		doc.pstate = sanitize('permanent_state')
		doc.ppost_office = sanitize('permanent_perm_post_office')
		doc.ppin_code = sanitize('permanent_pin')

		doc.name_of_employer = sanitize('name_of_employer')
		doc.department = sanitize('current_department')
		doc.cdesignation = sanitize('current_designation')
		doc.reports_to = sanitize('reports_to')
		doc.cname = sanitize('manager_name')
		doc.ccontact = sanitize('manager_contact_no')
		doc.cemail = sanitize('manager_email')
		doc.creference = sanitize('reference_taken')
		doc.address_of_employeer = sanitize('address_of_employer')
		doc.duties_and_reponsibilitiess = sanitize('duties_and_responsibilities')
		doc.reason_for_leavingg = sanitize('reason_for_leaving')
		doc.current_employment_type = sanitize('was_this_position')
		doc.agency_details = sanitize('agency_details')
		doc.phone_number = sanitize('phone_number')
		doc.current_salary = sanitize('current_salary')
		doc.first_salary_drawn = sanitize('first_salary_drawn')
		doc.telephone_number = sanitize('telephone_number')
		doc.email_id = sanitize('email_id')
		doc.employee_code = sanitize('employee_code')
		doc.in_india = bool(form_data.get('in_india'))
		doc.abroad = bool(form_data.get('abroad'))
		doc.is_form_submitted = form_data.get('is_form_submitted')

		doc.expected_salary = sanitize('expected_salary')
		doc.other_achievments = sanitize('other_achievments')
		doc.position = sanitize('position')
		doc.interviewed_location = sanitize('interviewed_location')
		doc.interviewed_date = convert_date(form_data.get('interviewed_date'))
		doc.interviewed_outcome = sanitize('interviewed_outcome')
		doc.related_employee = sanitize('related_employee')
		doc.related_employee_org = sanitize('related_employee_org')
		doc.related_employee_pos = sanitize('related_employee_pos')
		doc.related_employee_rel = sanitize('related_employee_rel')
		doc.professional_org = sanitize('professional_org')
		doc.political_org = sanitize('political_org')
		doc.specialised_training = sanitize('specialised_training')
		doc.share_your_thoughts = sanitize('additional_comments')

		years = form_data.get('period_years') or '0'
		months = form_data.get('current_period_months') or '0'
		doc.period_of_stay = f'{years} Years {months} Months'

		for field in ['payslip_month_1', 'payslip_month_2', 'payslip_month_3']:
			if form_data.get(field):
				filename = update_file(form_data[field], 'Job Applicant', docname) or ''
				setattr(doc, field, filename)

		doc.education_qualification = []
		for row in form_data.get('education_qualification', []):
			if row.get('course'):
				filename = update_file(row.get('attachments'), 'Job Applicant', docname) or ''
				doc.append('education_qualification', {
					'course': row.get('course'),
					'name_of_school_college': row.get('name_of_school_college'),
					'name_of_universityboard_of_exam': row.get('name_of_universityboard_of_exam'),
					'dates_attended_from': int(row.get('dates_attended_from')),
					'dates_attended_to': int(row.get('dates_attended_to')),
					'result': float(row.get('result')),
					'attachments': filename
				})

		doc.professional_certification = []
		for row in form_data.get('professional_certification', []):
			if row.get('course'):
				filename = update_file(row.get('attachments'), 'Job Applicant', docname) or ''
				doc.append('professional_certification', {
					'course': row.get('course'),
					'institute_name': row.get('institute_name'),
					'dates_attended_from': int(row.get('dates_attended_from')),
					'dates_attended_to': int(row.get('dates_attended_to')),
					'type_of_certification': row.get('type_of_certification'),
					'subject_major': row.get('subject_major'),
					'attachments': filename
				})

		doc.prev_emp_his = []
		for row in form_data.get('prev_emp_his', []):
			if row.get('name_of_org'):
				filename = update_file(row.get('attachments'), 'Job Applicant', docname) or ''
				doc.append('prev_emp_his', {
					'name_of_org': row.get('name_of_org'),
					'prev_designation': row.get('prev_designation'),
					'last_salary_drawn': row.get('last_salary_drawn'),
					'name_of_manager': row.get('name_of_manager'),
					'period_of_employment': row.get('period_of_employment'),
					'reason_for_leaving': row.get('reason_for_leaving'),
					'attachments': filename
				})

		doc.language_proficiency = []
		for row in form_data.get('language_proficiency', []):
			doc.append('language_proficiency', {
				'language': row.get('language'),
				'speak': row.get('speak'),
				'read': row.get('read'),
				'write': row.get('write')
			})

		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {'message': 'success', 'docname': doc.name}

	except Exception as e:
		frappe.log_error(
			title='Job Application Update Failed',
			message=f'Error updating applicant \'{docname}\'\nException: {str(e)}'
		)
		return {'message': str(e)}

@frappe.whitelist(allow_guest=True)
def update_file(filedata, doctype, docname):
	file_name = None
	if filedata and doctype and docname:
		filedata_list = filedata['files_data']
		for filedata_item in filedata_list:
			filedoc = save_file(
				filedata_item['filename'],
				filedata_item['dataurl'],
				doctype,
				docname,
				decode=True,
				is_private=0
			)
			file_name = filedoc.file_url
	frappe.db.commit()
	return file_name
