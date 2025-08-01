import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url, now_datetime
from frappe.utils import nowdate
from frappe.utils import get_url_to_form
from frappe.utils.password import encrypt
from frappe.model.naming import make_autoname
import os
from frappe.utils import today, getdate

@frappe.whitelist()
def autoname(doc, method):
	doc.name = make_autoname("JOB-APP-" + ".YYYY.-.####")

@frappe.whitelist()
def validate(doc, method):
	'''
		Method which trigger on validate of Job Applicant
	'''
	validate_job_applicant_details(doc)
	update_shortlisted_status_if_all_interviews_cleared(doc)

	if doc.status == 'Pending Document Upload' and doc.is_form_submitted:
		doc.status = 'Document Uploaded'

def validate_job_applicant_details(doc):
	'''
		Validate the Job Applicant against Job Opening requirements
	'''
	if doc.job_title:
		if frappe.db.exists('Job Opening', doc.job_title):
			job_opening_doc = frappe.get_doc('Job Opening', doc.job_title)

			# Fetching Minimum Experience
			expected_experience = float(job_opening_doc.min_experience) if job_opening_doc.min_experience else 0
			experience = float(doc.min_experience) if doc.min_experience else 0

def update_shortlisted_status_if_all_interviews_cleared(doc):
	'''
		Update Job Applicant status to 'Shortlisted from Interview'
		if all interview rounds are cleared and status is Interview Completed.
	'''
	if doc.status == 'Interview Completed':
		all_cleared = True
		for row in doc.applicant_interview_rounds:
			if row.interview_status != 'Cleared':
				all_cleared = False
				break

		if all_cleared:
			doc.status = 'Shortlisted from Interview'

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
				message=response,
				delayed= False
			)
			frappe.msgprint(f'Magic link sent to {email_id}')
			frappe.db.set_value('Job Applicant', applicant_id, 'status', 'Pending Document Upload')
			return link
		else:
			frappe.msgprint('Email Template "Job Applicant Follow Up" does not exist.', alert=True)

@frappe.whitelist()
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


@frappe.whitelist()
def validate_unique_application(doc, method):
	'''
	Method to validate that an applicant can only apply for a job opening once using the same email ID.

	'''
	if doc.email_id and doc.job_title:
		existing_applicant = frappe.db.exists(
			"Job Applicant",
			{
				"email_id": doc.email_id,
				"job_title": doc.job_title,
			}
		)
		if existing_applicant and existing_applicant != doc.name:
			frappe.throw(
				_("The applicant with email ID {0} has already applied for the job opening {1}.")
				.format(doc.email_id, doc.job_title)
			)

def fetch_designation(doc, method):
	if doc.job_title:
		# Fetch the designation from the Job Opening
		designation = frappe.db.get_value('Job Opening', doc.job_title, 'designation')
		if designation:
			doc.designation = designation
		else:
			frappe.throw(f"Designation not found for the selected Job Opening: {doc.job_title}")

def fetch_department(doc, method):
	if doc.job_title:
		# Fetch the designation from the Job Opening
		department = frappe.db.get_value('Job Opening', doc.job_title, 'department')
		if department:
			doc.department = department
		else:
			frappe.throw(f"Department not found for the selected Job Opening: {doc.job_title}")

@frappe.whitelist()
def calculate_and_validate_age(doc, method=None):
	"""
		Calculate and validate age for a Job Applicant.
	"""

	if isinstance(doc, str):
		doc = frappe.parse_json(doc)

	date_of_birth = doc.get("date_of_birth")
	if not date_of_birth:
		return None

	dob = getdate(date_of_birth)
	today_date = getdate(today())

	if dob > today_date:
		frappe.throw(_("Date of Birth cannot be in the future."))

	age = today_date.year - dob.year - ((today_date.month, today_date.day) < (dob.month, dob.day))

	if age < 18:
		frappe.throw(_("Applicants must be at least 18 years old to apply."))
	doc.age = age
	return age
