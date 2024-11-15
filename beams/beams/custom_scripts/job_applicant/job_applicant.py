import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url, now_datetime
from frappe.utils import nowdate
from frappe.utils import get_url_to_form
from frappe.utils.password import encrypt

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	user_roles = frappe.get_roles(user)

	if 'Administrator' in user_roles:
		return None

	if 'Interviewer' in user_roles:
		conditions = """(`tabJob Applicant`._assign like '%{user}%')""".format(user=user)
		return conditions
	return None

@frappe.whitelist()
def validate(doc, method):
	'''
		Method which trigger on validate of Job Applicant
	'''
	validate_job_applicant_details(doc)
	if doc.status == 'Pending Document Upload' and doc.is_form_submitted:
		doc.status = 'Document Uploaded'

def validate_job_applicant_details(doc):
	'''
		Validate the Job Applicant against Job Opening requirements
	'''
	if doc.job_title:
		if frappe.db.exists('Job Opening', doc.job_title):
			job_opening_doc = frappe.get_doc('Job Opening', doc.job_title)

			#Validating Minimum Experience
			expected_experience = float(job_opening_doc.min_experience) if job_opening_doc.min_experience else 0
			experience = float(doc.min_experience) if doc.min_experience else 0
			if job_opening_doc and expected_experience and (experience < expected_experience):
				frappe.throw(_('Applicant does not meet the required experience: <b>{0} years</b>').format(str(expected_experience)))

@frappe.whitelist()
def get_existing_local_enquiry_report(doc_name):
	'''
		Create a Local Enquiry Report if it doesn't already exist
	'''
	ler_id = None
	# Check if a Local Enquiry Report already exists for the given Job Applicant
	if frappe.db.exists('Local Enquiry Report', { 'job_applicant':doc_name }):
		ler_id = frappe.db.get_value('Local Enquiry Report', { 'job_applicant':doc_name })
	return ler_id

@frappe.whitelist()
def create_and_return_report(job_applicant):
	'''
        Create a Local Enquiry Report, show an alert message, and return its name
	'''
	if frappe.db.exists('Job Applicant', job_applicant):
		ler_doc = frappe.new_doc('Local Enquiry Report')
		ler_doc.job_applicant = job_applicant
		ler_doc.save(ignore_permissions=True)
		frappe.msgprint('Local Enquiry Report Created: <a href="{0}">{1}</a>'.format(
			get_url_to_form(ler_doc.doctype, ler_doc.name),
			ler_doc.name
		),alert=True,indicator='green')
		return ler_doc.name
	return None

@frappe.whitelist()
def send_magic_link(applicant_id):
	'''
        Sends a unique magic link to the specified job applicant's email for document upload.
        Args:
            applicant_name (str): The name of the job applicant.
        Returns:
            None
	'''
	if frappe.db.exists('Job Applicant', applicant_id):
		email_id, applicant_name = frappe.db.get_value('Job Applicant', applicant_id, ['email_id', 'applicant_name'])
		link = generate_magic_link(applicant_id)
		if frappe.db.exists('Email Template', 'Job Applicant Follow Up'):
			template = frappe.get_doc('Email Template', 'Job Applicant Follow Up')
			subject = frappe.render_template(template.subject, {'applicant_name': applicant_name})
			response = frappe.render_template(template.response, {
				'applicant_name': applicant_name,
				'magic_link': link
			})
			frappe.sendmail(
				recipients=[email_id],
				subject=subject,
				message=response
			)
			frappe.msgprint(f'Magic link sent to {email_id}')
			frappe.db.set_value('Job Applicant', applicant_id, 'status', 'Pending Document Upload')
			return 1
		else:
			frappe.msgprint('Email Template "Job Applicant Follow Up" does not exist.', alert=True)

def generate_magic_link(applicant_id):
	'''
        Generates and returns a magic link URL for the specified job applicant
        Args:
            applicant_name (str): The name of the job applicant
        Returns:
            str: The generated magic link URL
	'''
	link = '{0}/job_application_upload/upload_doc?applicant_id='.format(get_url())
	if frappe.db.exists('Job Applicant', applicant_id):
		encrypted_link = encrypt(applicant_id)
		link += encrypted_link
	return link

@frappe.whitelist()
def set_interview_rounds(doc, method):
	'''
		Method to set Interview Rounds to Job Applicant from Job Opening
	'''
	if frappe.db.exists('Job Opening', doc.job_title):
		job_opening_doc = frappe.get_doc('Job Opening', doc.job_title)
		if job_opening_doc.interview_rounds:
			for round in job_opening_doc.interview_rounds:
				doc.append('applicant_interview_rounds', {
					'interview_round': round.interview_round
				})
			doc.save()					

@frappe.whitelist()
def get_job_opening_location(job_opening):
	'''
		Method to get Location from Job Opening
	'''
	location = None
	if frappe.db.exists('Job Opening', job_opening):
		location = frappe.db.get_value('Job Opening', job_opening, 'preffered_location') or None
	return location
