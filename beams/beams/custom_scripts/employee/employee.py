import frappe
from frappe import _
from frappe.model.naming import make_autoname
from frappe.model.naming import set_name_by_naming_series
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, nowdate, add_days,today


@frappe.whitelist()
def create_event(employee_id=None, hod_user=None, target_doc=None):
	"""
	Create an Event document mapped from an Employee record, adding both the Employee and the HOD
	as participants in the Event.
	"""
	user = frappe.session.user
	if not employee_id:
		employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
	hod_user = hod_user or user
	hod_employee_id = frappe.get_value("Employee", {"user_id": hod_user}, "name")
	doc = get_mapped_doc("Employee", employee_id, {
		"Employee": {
			"doctype": "Event"
		}
	}, target_doc)
	employee_participant = doc.append("event_participants", {})
	employee_participant.reference_docname = employee_id
	employee_participant.reference_doctype = "Employee"
	hod_participant = doc.append("event_participants", {})
	hod_participant.reference_docname = hod_employee_id
	hod_participant.reference_doctype = "Employee"

	return doc

@frappe.whitelist()
def get_employee_name_for_user(user_id):
	'''
	Fetch the Employee name associated with the given user_id.
	'''
	employee_name = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
	return employee_name

def assign_leave_policy_on_joining(doc, method):
	"""
	Create a Leave Policy Assignment for the Employee using the leave_policy
	set in the Employee record, based on the Joining Date.
	"""
	if not doc.leave_policy:
		frappe.log_error(
			f"Leave Policy not set for Employee {doc.name}",
			"Assign Leave Policy Error"
		)
		return

	# Create Leave Policy Assignment
	leave_policy_assignment = frappe.new_doc("Leave Policy Assignment")
	leave_policy_assignment.employee = doc.name
	leave_policy_assignment.company = doc.company
	leave_policy_assignment.leave_policy = doc.leave_policy
	leave_policy_assignment.assignment_based_on = "Joining Date"
	leave_policy_assignment.effective_from = doc.date_of_joining
	leave_policy_assignment.insert(ignore_mandatory=True)

def validate(doc, method):
	"""
		Automatically set the relieving_date based on resignation_letter_date and notice_number_of_days.
	"""
	if doc.resignation_letter_date and doc.notice_number_of_days:
		doc.relieving_date = add_days(getdate(doc.resignation_letter_date), doc.notice_number_of_days)

@frappe.whitelist()
def get_notice_period(employment_type, job_applicant=None, current_notice_period=None):
	'''
	Fetch the notice period based on the employment type and Beams HR Settings.

	Conditions:
	- If current notice_number_of_days is set, return the existing notice period
	- If employment type matches Permanent Employment Type in Beams HR Settings:
	  - First check Appointment Letter
	  - If no Appointment Letter, fetch from Employment Type
	- For other employment types :
	  - Fetch notice period directly from Employment Type
	'''

	# Get Permanent Employment Type from Beams HR Settings
	permanent_emp_type = frappe.db.get_single_value('Beams HR Settings', 'permanent_employment_type')

	notice_period = None

	# Check if the employment type matches Permanent Employment Type
	if employment_type == permanent_emp_type and job_applicant:
		# Check if an Appointment Letter exists for the Job Applicant
		appointment_letter = frappe.get_value('Appointment Letter',
			{'job_applicant': job_applicant}, 'notice_period')

		if appointment_letter:
			# Fetch the notice period from the Appointment Letter
			notice_period = appointment_letter

	# If no Appointment Letter notice period found or not Permanent Employment Type,
	# fetch from Employment Type
	if not notice_period:
		notice_period = frappe.get_value('Employment Type',
			{'name': employment_type}, 'notice_period')

	return notice_period

def autoname(doc, method):
	'''
		Method to set Employee ID
	'''
	employee_naming_by_department = frappe.db.get_single_value('HR Settings', 'employee_naming_by_department')
	if employee_naming_by_department:
		if not doc.department:
			frappe.throw(_('Department is required to create Employee'))
		department_abbr = frappe.db.get_value('Department', doc.department, 'abbreviation')
		if not department_abbr:
			frappe.throw(_('Abbreviation is missing for Department : {0} is required to create Employee'.format(doc.department)))
		doc.name = get_next_employee_id(department_abbr)
	doc.employee = doc.name

def get_next_employee_id(department_abbr):
	'''
		Method to get next Employee ID
	'''
	p = f"MB/{department_abbr}/"
	last = frappe.db.get_all(
		"Employee",
		filters={"name": ["like", f"{p}%"]},
		order_by="creation desc",
		pluck="name",
		limit=1
	)
	last_no = int(last[0].split("/")[-1]) if last else 0
	return f"{p}{last_no + 1:03d}"

def validate_offer_dates(doc, method):
	"""Validate Employee fields before saving/submitting."""

	today_date = getdate(today())

	# Ensure Final Confirmation Date is after Scheduled Confirmation Date
	if doc.scheduled_confirmation_date and doc.final_confirmation_date:
		if getdate(doc.final_confirmation_date) < getdate(doc.scheduled_confirmation_date):
			frappe.throw(_("Confirmation Date must be after Offer Date."))

def manage_user_status(doc, method=None):
	"""
	Automatically enable or disable a linked User account
	based on the Employee's status.
	- If Employee is 'Active' → Enable User
	- If Employee is 'Inactive', 'Suspended', 'Left' → Disable User
	"""

	if not doc.user_id:
		return

	user_enabled_status = frappe.db.get_value("User", doc.user_id, "enabled")

	if doc.status == "Active":
		if user_enabled_status == 0:
			frappe.db.set_value("User", doc.user_id, "enabled", 1)

	elif doc.status in ["Inactive", "Suspended", "Left"]:
		if user_enabled_status == 1:
			frappe.db.set_value("User", doc.user_id, "enabled", 0)

def create_notification_log(subject, for_users, doc_type, doc_name, email_content, from_user="Administrator"):
	"""
	Function to create Notification Logs for given users.
	"""
	for user in for_users:
		user_id = frappe.db.get_value("User", {"email": user}, "name") or user
		frappe.get_doc({
			"doctype": "Notification Log",
			"subject": subject,
			"for_user": user_id,
			"type": "Alert",
			"document_type": doc_type,
			"document_name": doc_name,
			"from_user": from_user,
			"email_content": email_content
		}).insert(ignore_permissions=True)

def get_context(emp, initiative_days, deadline_date, notify_days_before=None):
	"""
	Generate common context for rendering templates.
	"""
	return {
		"employee_name": emp.employee_name,
		"employee_id": emp.name,
		"department": emp.department,
		"date_of_joining": emp.date_of_joining,
		"appraisal_initiation_days": initiative_days,
		"deadline_date": deadline_date,
		"notify_days_before": notify_days_before,
	}


def send_joining_based_appraisal_notification(doc, method=None):
	"""
	Triggered when an Employee is created.
	Sends a notification to HR reminding them to set up appraisal.
	"""
	if doc.appraisal_template or not doc.date_of_joining:
		return

	settings = frappe.get_single("Beams HR Settings")
	template_name = settings.joining_based_appraisal_notification_template
	initiative_days = settings.appraisal_initiative_days

	if not template_name or not initiative_days:
		return

	joining_date = getdate(doc.date_of_joining)
	deadline_date = add_days(joining_date, initiative_days)
	hr_emails = []

	hr_users = frappe.db.get_all("Has Role", filters={"role": "HR Manager"}, pluck="parent")
	for u in hr_users:
		email = frappe.db.get_value("User", u, "email")
		if email:
			hr_emails.append(email)

	if not hr_emails:
		return

	template = frappe.db.get_value(
		"Email Template",
		template_name,
		["subject", "response"],
		as_dict=True,
	)
	context = get_context(doc, initiative_days, deadline_date)
	subject = frappe.render_template(template.subject or "", context)
	email_content = frappe.render_template(template.response or template.message or "", context)
	frappe.sendmail(
		recipients=hr_emails,
		subject=subject,
		message=email_content
	)
	create_notification_log(subject, hr_emails, "Employee", doc.name, email_content, from_user=frappe.session.user)

def send_pre_deadline_appraisal_reminder():
	"""
	Daily scheduler job to check employees whose appraisal_template
	is not set and send HR a pre-deadline notification.
	"""

	settings = frappe.get_single("Beams HR Settings")
	template_name = settings.re_deadline_hr_notification_template
	initiative_days = settings.appraisal_initiative_days
	notify_days_before = settings.hr_notification_days_before_deadline

	if not template_name or not initiative_days or not notify_days_before:
		return

	today = getdate(nowdate())
	employees = frappe.get_all(
		"Employee",
		filters={"status": "Active", "appraisal_template": ["is", "not set"]},
		fields=["name", "employee_name", "date_of_joining", "department"]
	)

	for emp in employees:
		if not emp.date_of_joining:
			continue

		doj = getdate(emp.date_of_joining)
		deadline_date = add_days(doj, initiative_days)
		notify_date = add_days(deadline_date, -notify_days_before)

		if today == notify_date:
			already_sent = frappe.db.exists(
				"Notification Log",
				{
					"document_type": "Employee",
					"document_name": emp.name,
					"subject": ["like", f"[Pre-Deadline][{emp.name}][{notify_date}]%"]
				}
			)
			if already_sent:
				continue

			hr_emails = []
			hr_users = frappe.db.get_all("Has Role", filters={"role": "HR Manager"}, pluck="parent")
			for u in hr_users:
				email = frappe.db.get_value("User", u, "email")
				if email:
					hr_emails.append(email)

			if not hr_emails:
				continue

			template = frappe.db.get_value(
				"Email Template",
				template_name,
				["subject", "response"],
				as_dict=True,
			)
			context = get_context(emp, initiative_days, deadline_date, notify_days_before)
			subject = frappe.render_template(template.subject or "", context)
			email_content = frappe.render_template(template.response or template.message or "", context)
			frappe.sendmail(
				recipients=hr_emails,
				subject=subject,
				message=email_content
			)
			unique_subject = f"[Pre-Deadline][{emp.name}][{notify_date}] {subject}"
			create_notification_log(unique_subject, hr_emails, "Employee", emp.name, email_content)

def send_appraisal_escalation():
	"""
	Daily scheduler job to check employees whose appraisal_template
	is not set and send HR an escalation notification.
	"""

	settings = frappe.get_single("Beams HR Settings")
	template_name = settings.appraisal_creation_escalation_template
	initiative_days = settings.appraisal_initiative_days

	if not template_name or not initiative_days:
		return

	today = getdate(nowdate())

	employees = frappe.get_all(
		"Employee",
		filters={"status": "Active", "appraisal_template": ["is", "not set"]},
		fields=["name", "employee_name", "date_of_joining", "department"]
	)

	for emp in employees:
		if not emp.date_of_joining:
			continue

		doj = getdate(emp.date_of_joining)
		deadline_date = add_days(doj, initiative_days)

		if today == deadline_date:
			already_sent = frappe.db.exists(
				"Notification Log",
				{
					"document_type": "Employee",
					"document_name": emp.name,
					"subject": ["like", f"[Escalation][{emp.name}]%"]
				}
			)
			if already_sent:
				continue

			hr_emails = []
			hr_users = frappe.db.get_all("Has Role", filters={"role": "HR Manager"}, pluck="parent")
			for u in hr_users:
				email = frappe.db.get_value("User", u, "email")
				if email:
					hr_emails.append(email)

			if not hr_emails:
				continue

			template = frappe.db.get_value(
				"Email Template",
				template_name,
				["subject", "response"],
				as_dict=True,
			)
			context = get_context(emp, initiative_days, deadline_date)
			subject = frappe.render_template(template.subject or "", context)
			email_content = frappe.render_template(template.response or template.message or "", context)
			frappe.sendmail(
				recipients=hr_emails,
				subject=subject,
				message=email_content
			)
			unique_subject = "[Escalation][{emp_name}] {subject}".format(emp_name=emp.name, subject=subject)
			create_notification_log(unique_subject, hr_emails, "Employee", emp.name, email_content)

def create_ceo_appraisal_alert_template():
	"""
	Daily scheduler job to check employees whose appraisal_template
	is not set and send CEO an escalation notification.
	"""

	settings = frappe.get_single("Beams HR Settings")
	template_name = settings.ceo_appraisal_alert_template
	initiative_days = settings.appraisal_initiative_days

	if not template_name or not initiative_days:
		return

	today = getdate(nowdate())

	employees = frappe.get_all(
		"Employee",
		filters={"status": "Active", "appraisal_template": ["is", "not set"]},
		fields=["name", "employee_name", "date_of_joining", "department"]
	)

	for emp in employees:
		if not emp.date_of_joining:
			continue

		doj = getdate(emp.date_of_joining)
		deadline_date = add_days(doj, initiative_days)

		if today >= deadline_date:
			already_sent = frappe.db.exists(
				"Notification Log",
				{
					"document_type": "Employee",
					"document_name": emp.name,
					"subject": ["like", f"[Escalation][{emp.name}]%"]
				}
			)
			if already_sent:
				continue

			ceo_emails = []
			ceo_users = frappe.db.get_all("Has Role", filters={"role": "CEO"}, pluck="parent")
			for u in ceo_users:
				email = frappe.db.get_value("User", u, "email")
				if email:
					ceo_emails.append(email)

			if not ceo_emails:
				continue

			template = frappe.db.get_value(
				"Email Template",
				template_name,
				["subject", "response"],
				as_dict=True,
			)
			context = get_context(emp, initiative_days, deadline_date)
			subject = frappe.render_template(template.subject or "", context)
			email_content = frappe.render_template(template.response or template.message or "", context)
			frappe.sendmail(
				recipients=ceo_emails,
				subject=subject,
				message=email_content
			)
			unique_subject = f"[Escalation][{emp.name}] {subject}"
			create_notification_log(unique_subject, ceo_emails, "Employee", emp.name, email_content)

def validate_assessment_officer(doc, method=None):
	officers = doc.assessment_officers or []
	if sum(1 for row in officers if row.is_primary) > 1:
		frappe.throw("Only one Primary Assessment Officer can be selected.")

@frappe.whitelist()
def update_next_appraisal_dates_and_create_appraisal():
	"""
	Daily Scheduler:
	- For each active employee, check if next_appraisal_date + days <= today.
	- If overdue, update next_appraisal_date and create appraisal in Draft.
	"""
	days = frappe.db.get_single_value("Beams HR Settings", "days_for_next_appraisal_creation")
	today_date = getdate(today())

	employees = frappe.get_all(
		"Employee",
		filters={"status": "Active"},
		fields=["name", "next_appraisal_date", "employee_name", "appraisal_template"]
	)

	for emp in employees:
		if not emp.next_appraisal_date:
			continue

		next_appraisal_date = getdate(emp.next_appraisal_date)
		next_cycle_date = add_days(next_appraisal_date, days)

		if next_cycle_date <= today_date:
			frappe.db.set_value("Employee", emp.name, "next_appraisal_date", next_cycle_date)
			frappe.db.commit()

			create_appraisal_if_not_exists(
				emp=frappe._dict(emp),
				start_date=next_cycle_date,
				end_date=add_days(next_cycle_date, days - 1)
			)

def create_appraisal_if_not_exists(emp, start_date, end_date):
	"""
	Create a Draft appraisal if template exists and no overlapping appraisal exists.
	Maps goals from Appraisal Template into appraisal_kra table.
	Returns True if appraisal was created, False otherwise.
	"""
	if not emp.appraisal_template:
		return False

	existing = frappe.get_all(
		"Appraisal",
		filters={
			"employee": emp.name,
			"docstatus": ["!=", 2],
			"start_date": ["<=", end_date],
			"end_date": [">=", start_date],
		},
		limit=1
	)

	if existing:
		return False

	template_goals = frappe.get_all(
		"Appraisal Template Goal",
		filters={"parent": emp.appraisal_template},
		fields=["key_result_area", "per_weightage"]
	)

	appraisal_doc = frappe.get_doc({
		"doctype": "Appraisal",
		"employee": emp.name,
		"appraisal_template": emp.appraisal_template,
		"start_date": start_date,
		"end_date": end_date,
		"consent_received": 0 
	})

	for goal in template_goals:
		appraisal_doc.append("appraisal_kra", {
			"kra": goal.key_result_area,
			"per_weightage": goal.per_weightage
		})

	appraisal_doc.insert(ignore_permissions=True)
	return True

def employee_on_update(doc, method):
	"""
	Triggered when Employee is saved.
	- If next_appraisal_date and appraisal_template are set,
	  create appraisal instantly if it doesn't exist already.
	"""
	if doc.next_appraisal_date and doc.appraisal_template:
		days = frappe.db.get_single_value("Beams HR Settings", "days_for_next_appraisal_creation") or 365
		start_date = getdate(doc.next_appraisal_date)
		end_date = add_days(start_date, days - 1)
		existing_appraisal = frappe.get_all(
			"Appraisal",
			filters={
				"employee": doc.name,
				"start_date": ["<=", end_date],
				"end_date": [">=", start_date],
			},
		)
		if not existing_appraisal:
			create_appraisal_if_not_exists(
				emp=doc,
				start_date=start_date,
				end_date=end_date
			)

def populate_employee_details_from_applicant(doc, method):
	"""
		Populate Employee addresses, education, and employment history from the linked Job Applicant
	"""
	if not doc.job_applicant:
		return
	job_applicant = frappe.get_doc("Job Applicant", doc.job_applicant)
	current_address_parts = [
		job_applicant.house_no_name,
		job_applicant.street_road,
		job_applicant.locality_village,
		job_applicant.city,
		job_applicant.district,
		job_applicant.state,
		job_applicant.post_office
	]
	doc.current_address = "\n ".join([part for part in current_address_parts if part])
	doc.pincode = job_applicant.pin_code
	permanent_address_parts = [
		job_applicant.phouse_no_name,
		job_applicant.pstreet_road,
		job_applicant.plocality_village,
		job_applicant.pcity,
		job_applicant.pdistrict,
		job_applicant.pstate,
		job_applicant.ppost_office
	]
	doc.permanent_address = "\n ".join([part for part in permanent_address_parts if part])
	doc.permanent_pin_code = job_applicant.ppin_code
	doc.aadhar_id = job_applicant.aadhar_number
	doc.salutation = job_applicant.salutation
	doc.education_qualification = []
	for row in job_applicant.education_qualification:
		doc.append("education_qualification", {
			"course": row.course,
			"name_of_school_college": row.name_of_school_college,
			"name_of_universityboard_of_exam": row.name_of_universityboard_of_exam,
			"dates_attended_from": row.dates_attended_from,
			"dates_attended_to": row.dates_attended_to,
			"result": row.result,
			"attachments": row.attachments
		})
	doc.previous_employment_history = []
	for row in job_applicant.prev_emp_his:
		doc.append("previous_employment_history", {
			"name_of_org": row.name_of_org,
			"prev_designation": row.prev_designation,
			"last_salary_drawn": row.last_salary_drawn,
			"period_of_employment": row.period_of_employment,
			"name_of_manager": row.name_of_manager,
			"reason_for_leaving": row.reason_for_leaving,
			"attachments": row.attachments
		})

	if job_applicant.job_title:
		employment_type = frappe.db.get_value("Job Opening", job_applicant.job_title, "employment_type")
		if employment_type:
			doc.employment_type = employment_type
	doc.save()

	assign_leave_policy_on_joining(doc, method)
