import frappe
from frappe.utils import nowdate, add_days, format_date

def notify_manager_unplanned_absence():
	'''
	Send a reminder to the reports_to if an employee was absent but did not apply for leave.
	The reminder is based on the value in Absence Reminder Duration and only if Enable Absence Reminders is checked.
	'''
	hr_settings = frappe.get_single("Beams HR Settings")
	absence_reminder_duration = hr_settings.absence_reminder_duration
	if not absence_reminder_duration:
		return
	email_template_name = hr_settings.absence_reminder_template
	if not email_template_name:
		return
	email_template = frappe.get_doc("Email Template", email_template_name)
	target_date = add_days(nowdate(), -absence_reminder_duration)
	absent_employees = frappe.get_all(
		"Attendance",
		filters={"attendance_date": target_date, "status": "Absent"},
		fields=["employee", "employee_name", "attendance_date"]
	)
	if absent_employees:
		for employee in absent_employees:
			leave_exists = frappe.db.exists(
				"Leave Application",
				{
					"employee": employee["employee"],
					"from_date": ("<=", employee["attendance_date"]),
					"to_date": (">=", employee["attendance_date"]),
					"docstatus": 1,
				}
			)
			if not leave_exists:
				# Fetch the Employment Type for the employee
				employment_type = frappe.db.get_value(
					"Employee", employee["employee"], "employment_type"
				)

				# Fetch the penalty_leave_type from Employment Type doctype
				leave_type = frappe.db.get_value(
					"Employment Type", employment_type, "penalty_leave_type"
				)

				# If no penalty_leave_type is found, set leave type to Leave Without Pay (LWOP)
				if not leave_type:
					leave_type = "Leave Without Pay"  # Default to LWOP if no penalty leave type is set

				# Create a new Leave Application document
				leave_application = frappe.new_doc("Leave Application")
				leave_application.employee = employee["employee"]
				leave_application.leave_type = leave_type
				leave_application.from_date = employee["attendance_date"]
				leave_application.to_date = employee["attendance_date"]
				leave_application.status = "Approved"
				leave_application.save()

				leave_application.submit()


				# Notify the supervisor
				reports_to = frappe.db.get_value("Employee", employee["employee"], "reports_to")
				if reports_to:
					reports_to_email, reports_to_name = frappe.db.get_value("Employee", reports_to, ['user_id', 'employee_name'])
					if reports_to_email:
						context_data = {
							"employee_name": employee["employee_name"],
							"employee_id": employee["employee"],
							"attendance_date": employee["attendance_date"],
							"reports_to_name": reports_to_name
						}
						subject = frappe.render_template(email_template.subject, context_data)
						message = frappe.render_template(email_template.response, context_data)
						frappe.sendmail(
							recipients=[reports_to_email],
							subject=subject,
							message=message
						)


def remind_employee_unplanned_absence():
	"""Send a reminder to employees who were absent but did not apply for leave."""

	hr_settings = frappe.get_single("Beams HR Settings")
	if not hr_settings.leave_application_reminder_duration:
		return
	absence_reminder_duration = hr_settings.leave_application_reminder_duration
	target_date = add_days(nowdate(), -absence_reminder_duration)
	absent_employees = frappe.get_all(
		"Attendance",
		filters={"attendance_date": target_date, "status": "Absent"},
		fields=["employee", "employee_name", "attendance_date"]
	)
	if absent_employees:
		for employee in absent_employees:

			# Check if a leave application exists for the absence
			leave_exists = frappe.db.exists(
				"Leave Application",
				{
					"employee": employee["employee"],
					"from_date": ("<=", employee["attendance_date"]),
					"to_date": (">=", employee["attendance_date"]),
					"docstatus": 1,  # Leave application should be submitted
				}
			)

			if  not leave_exists:
				send_employee_absence_email(employee)

def send_employee_absence_email(employee):
	"""Send an email reminder to the absent employee to submit a leave application."""
	hr_settings = frappe.get_single("Beams HR Settings")
	email_template_name = hr_settings.leave_application_template
	if not email_template_name:
		return
	email_template = frappe.get_doc("Email Template", email_template_name)

	# Prepare context data for rendering the template
	context_data = {
		"employee_name": employee["employee_name"],
		"employee_id": employee["employee"],
		"attendance_date": employee["attendance_date"]
	}

	subject = frappe.render_template(email_template.subject, context_data)
	message = frappe.render_template(email_template.response, context_data)

	# Get the employee's email (user_id field in the Employee DocType)
	email = frappe.db.get_value("Employee", employee["employee"], "user_id")

	if email:
		# Send email to the employee
		frappe.sendmail(
			recipients=[email],
			subject=subject,
			message=message
		)
		frappe.msgprint(f"Reminder email sent to {employee['employee_name']} ({email}).")
	else:
		frappe.log_error(
			f"Email not found for employee {employee['employee_name']} ({employee['employee']})",
			"Absence Reminder"
		)
