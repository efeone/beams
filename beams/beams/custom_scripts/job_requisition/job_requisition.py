import json
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import now_datetime, get_url_to_form
from datetime import datetime,date

@frappe.whitelist()
def create_job_opening_from_job_requisition(doc, method):
	'''
		Create a Job Opening when the Job Requisition is approved.
	'''
	if doc.workflow_state == 'Approved':
		if not frappe.db.exists('Job Opening', { 'job_requisition':doc.name }):
			job_opening = frappe.new_doc('Job Opening')
			job_opening.job_title = doc.job_title
			job_opening.designation = doc.designation
			job_opening.status = 'Open'
			job_opening.posted_on = now_datetime()
			job_opening.department = frappe.get_value("Employee", doc.requested_by, "department")
			job_opening.employment_type = doc.employment_type
			job_opening.job_requisition = doc.name
			# Setting Minimum Educational Qualification
			for qualification in doc.min_education_qual:
				job_opening.append('min_education_qual', {
					"qualification": qualification.qualification
				})
			job_opening.min_experience = doc.min_experience
			job_opening.job_requisition_id_ = doc.name
			job_opening.no_of_positions = doc.no_of_positions
			job_opening.no_of_days_off = doc.no_of_days_off
			job_opening.preffered_location = doc.location
			job_opening.publish = doc.publish_on_job_opening
			job_opening.travel_required = doc.travel_required
			job_opening.driving_license_needed = doc.driving_license_needed
			job_opening.license_type = doc.license_type
			job_opening.is_work_shift_needed = doc.is_work_shift_needed
			#Setting Skill Proficiency
			for skill in doc.skill_proficiency:
				job_opening.append('skill_proficiency', {
					"skill": skill.skill,
					"proficiency": skill.proficiency
				})
			#Setting Language Proficiency
			for language in doc.language_proficiency:
				job_opening.append('language_proficiency', {
					"language": language.language,
					"speak": language.speak,
					"write": language.write,
					"read": language.read
				})
			# Setting Interview Rounds
			for interview_round in doc.interview_rounds:
				job_opening.append('interview_rounds', {
					"interview_round": interview_round.interview_round
				})
			job_opening.description = doc.description
			job_opening.upper_range = doc.expected_compensation
			# Insert the Job Opening document
			job_opening.insert()
			frappe.msgprint(
				'Job Opening Created: <a href="{0}">{1}</a>'.format(get_url_to_form(job_opening.doctype, job_opening.name), job_opening.name),
				alert=True, indicator='green')

@frappe.whitelist()
def on_update(doc, method=None):
	'''
		Method triggered after the document is updated.
		It checks if the workflow state has changed to "Cancelled" or "On Hold".
	'''
	# Fetch the document state before saving
	old_doc = doc.get_doc_before_save()

	# Check if the old workflow state is different from the new one and if the new state is "Cancelled" or "On Hold"
	if old_doc and old_doc.workflow_state != doc.workflow_state and doc.workflow_state in ["Cancelled", "On Hold"]:
		close_job_openings(doc)

@frappe.whitelist()
def close_job_openings(doc):
	'''
		Close the linked Job Opening when the Job Requisition is cancelled or or "On Hold".
	'''
	job_openings = frappe.db.get_all('Job Opening', {'job_requisition': doc.name, 'status':['!=', 'Closed'] })
	for job_opening in job_openings:
		frappe.db.set_value('Job Opening', job_opening.name, 'status', 'Closed')
		frappe.db.set_value('Job Opening', job_opening.name, 'closed_on',  now_datetime())
		frappe.msgprint('Job Opening {0} has been closed'.format(job_opening.name), alert=True, indicator='green')

@frappe.whitelist()
def get_template_content(template_name, doc):
	'''
		This function fetches the Job Description Template and renders its content dynamically
		using the details of the Job Requisition document, returning the formatted job description
		for display.
	'''
	rendered_description = ''
	if frappe.db.exists('Job Description Template', template_name):
		if isinstance(doc, str):
			doc = frappe.parse_json(doc)
		description = frappe.db.get_value('Job Description Template', template_name, 'description')
		if description:
			rendered_description = frappe.render_template(description, doc)
	return rendered_description

@frappe.whitelist()
def validate_expected_by(doc, method=None):
	'''Ensure that 'Expected By' date is today or in the future.'''

	if doc.expected_by:
		if isinstance(doc.expected_by, str):
			expected_date = datetime.strptime(doc.expected_by, "%Y-%m-%d").date()
		elif isinstance(doc.expected_by, date):
			expected_date = doc.expected_by
		else:
			raise ValueError("Invalid type for expected_by. Expected a string or date object.")

		today = datetime.today().date()

		if expected_date < today:
			frappe.throw("Expected By date must be a future date.")

@frappe.whitelist()			
def validate_fields(doc, method):
	'''Ensure that 'Job Title' and 'Expected Compensation' are provided if the user has the 'HR Manager' role.'''

	if "HR Manager" in frappe.get_roles(frappe.session.user):
		if not doc.job_title:
			frappe.throw("Job Title is required for HR Managers.")

		if not doc.expected_compensation or doc.expected_compensation <= 0:
			frappe.throw("Expected Compensation (Yearly) must be greater than 0.")
