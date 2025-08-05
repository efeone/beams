# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe import _ 
from frappe.utils import get_datetime, now_datetime

class EmployeeInterviewTool(Document):
	pass

@frappe.whitelist()
def create_bulk_interviews(applicants):
	'''
		Creates multiple Interview documents for a list of job applicants, skipping those with existing interviews.

	'''
	applicants = json.loads(applicants)
	created_interviews = []
	existing_interviews = []

	for app in applicants:
		interview_round = app.get('interview_round')
		scheduled_on = app.get('scheduled_on')
		from_time = app.get('from_time')
		to_time = app.get('to_time')

		scheduled_datetime = get_datetime(f"{scheduled_on} {from_time}")
		now = now_datetime()

		if scheduled_datetime < now:
			frappe.throw(_("Interview date and time cannot be in the past for applicant: {0}").format(app.get('applicant_name')))

		if not (interview_round and scheduled_on and from_time and to_time):
			frappe.throw(
				_("Missing required scheduling fields. Please ensure 'Interview Round', 'Scheduled On', 'From Time', and 'To Time' are all filled.")
			)

		interview_round_doc = frappe.get_doc('Interview Round', interview_round)
		interviewers = interview_round_doc.get('interviewers')

		if frappe.db.exists('Interview', {
			'job_applicant': app.get('job_applicant'),
			'interview_round': interview_round
		}):
			existing_interviews.append(app.get('job_applicant'))
			continue

		interview = frappe.get_doc({
			'doctype': 'Interview',
			'job_applicant': app.get('job_applicant'),
			'applicant_name': app.get('applicant_name'),
			'designation': app.get('designation'),
			'department': app.get('department'),
			'interview_round': interview_round,
			'scheduled_on': scheduled_on,
			'from_time': from_time,
			'to_time': to_time
		})

		for i in interviewers:
			interviewer_id = getattr(i, 'employee', None) or getattr(i, 'user', None)
			if interviewer_id:
				interview.append('interview_details', {
					'interviewer': interviewer_id
				})

		interview.insert()
		created_interviews.append({
			"interview": interview.name,
			"job_applicant": app.get("job_applicant"),
			"applicant_name": app.get("applicant_name")
		})

	return {
	"created": created_interviews,
	"skipped_applicants": existing_interviews
	}

@frappe.whitelist()
def create_bulk_ler(applicants):
	"""
	Creates multiple Local Enquiry Report documents for selected job applicants,
	skipping those for whom a report already exists.
	"""
	applicants = json.loads(applicants)
	created_lers = []
	existing_lers = []

	for app in applicants:
		job_applicant = app.get("job_applicant")
		applicant_name = app.get("applicant_name")

		# Check if LER already exists
		if frappe.db.exists("Local Enquiry Report", {"job_applicant": job_applicant}):
			existing_lers.append(applicant_name or job_applicant)
			continue

		# Create LER
		ler = frappe.get_doc({
			"doctype": "Local Enquiry Report",
			"job_applicant": job_applicant,
			"job_applicant_name": applicant_name,
		})

		ler.insert()
		created_lers.append({
			"ler": ler.name,
			"job_applicant": job_applicant,
			"applicant_name": applicant_name
		})

	return {
		"created": created_lers,
		"skipped_applicants": existing_lers
	}

@frappe.whitelist()
def fetch_filtered_job_applicants(filters=None):
	"""
	Fetch job applicants based on filters like job_title, department, designation, status.
	"""
	if isinstance(filters, str):
		filters = frappe.parse_json(filters)

	if not isinstance(filters, dict):
		frappe.throw(_("Invalid filter format"))

	try:
		applicants = frappe.get_all(
			'Job Applicant',
			filters=filters,
			fields=['name', 'applicant_name', 'designation', 'status','department', 'location'],
			limit_page_length=50
		)
		return applicants

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Failed to fetch job applicants"))

@frappe.whitelist()
def reschedule_interviews(applicants, interview_round, scheduled_on, from_time, to_time):
	"""
		Reschedules existing Interview documents for given job applicants and interview round.
	"""
	if isinstance(applicants, str):
		applicants = json.loads(applicants)

	rescheduled = []

	for app_id in applicants:
		interviews = frappe.get_all("Interview", filters={
			"job_applicant": app_id,
			"interview_round": interview_round
		})

		for i in interviews:
			doc = frappe.get_doc("Interview", i.name)
			doc.scheduled_on = scheduled_on
			doc.from_time = from_time
			doc.to_time = to_time
			doc.save()
			rescheduled.append(i.name)
