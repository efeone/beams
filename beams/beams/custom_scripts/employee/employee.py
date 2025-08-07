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

@frappe.whitelist()
def after_insert(doc, method):
	"""
		Triggered after an Employee record is created.
		Fetches the default leave policy and leave period from Beams HR Settings,
		validates the configurations, and creates & submits a Leave Policy Assignment.
	"""
	# Fetch default leave policy and leave period from Beams HR Settings
	leave_policy = frappe.db.get_single_value('Beams HR Settings', 'default_leave_policy')
	leave_period = frappe.db.get_single_value('Beams HR Settings', 'leave_period')

	if not leave_policy or not leave_period:
		return

	# Fetch leave period details
	leave_period_details = frappe.db.get_value(
		'Leave Period',
		leave_period,
		['from_date', 'to_date'],
		as_dict=True
	)

	# Skip if leave period details are missing
	if not leave_period_details:
		return

	if not doc.name:
		return

	# Create Leave Policy Assignment
	leave_policy_assignment = frappe.get_doc({
		'doctype': 'Leave Policy Assignment',
		'employee': doc.name,
		'leave_policy': leave_policy,
		'leave_period': leave_period,
		'assignment_based_on': 'Leave Period',
		'effective_from': leave_period_details['from_date'],
		'effective_to': leave_period_details['to_date'],
	})

	# Save and submit the leave policy assignment
	leave_policy_assignment.insert()
	leave_policy_assignment.submit()


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
	series_prefix = "MB/{0}/".format(department_abbr)
	next_employee_id = '{0}1'.format(series_prefix)
	employees = frappe.db.get_all('Employee', { 'name': ['like', '%{0}%'.format(series_prefix)] }, order_by='name desc', pluck='name')
	if employees:
		employee_id = employees[0]
		employee_id = employee_id.replace(series_prefix, "")
		employee_count = int(employee_id)
		next_employee_id = '{0}{1}'.format(series_prefix, str(employee_count+1))
	return next_employee_id


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
