import frappe
from frappe.utils import nowdate, add_days, format_date

def send_absence_reminder():
    '''
    Send a reminder to the reports_to if an employee was absent but did not apply for leave.
    If the employee was absent and did not apply for leave, a leave application is created automatically.
    '''
    target_date = add_days(nowdate(), -2)
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

            # If no leave exists, create a leave application
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
                leave_application.save()

                # Notify the supervisor
                reports_to = frappe.db.get_value("Employee", employee["employee"], "reports_to")
                if reports_to:
                    reports_to_email = frappe.db.get_value("Employee", reports_to, "user_id")
                    if reports_to_email:
                        subject = f"Reminder: No Leave Application for Absent Employee"
                        message = f"""
                        <p>Dear {reports_to},</p>
                        <p>{employee['employee_name']} ({employee['employee']}) was absent on {employee['attendance_date']}
                        and has not submitted a leave application.</p>
                        <p>Please follow up with {employee['employee_name']} for further actions.</p>
                        <p>Best regards,<br>HR Team</p>
                        """
                        frappe.sendmail(
                            recipients=reports_to_email,
                            subject=subject,
                            message=message
                        )

def send_absent_reminder():
    """Send a reminder to employees who were absent but did not apply for leave."""

    # Get the date for yesterday
    target_date = add_days(nowdate(), -1)  # Yesterday

    # Fetch employees who were absent yesterday
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

            if not leave_exists:
                # Send a reminder to the employee who was absent
                send_reminder_email(employee)

def send_reminder_email(employee):
    """Send an email reminder to the absent employee to submit a leave application."""

    # Prepare email content
    subject = f"Reminder: Submit Leave Application for Absence on {format_date(employee['attendance_date'])}"
    message = f"""
    <p>Dear {employee['employee_name']},</p>
    <p>You were marked as <strong>Absent</strong> on {format_date(employee['attendance_date'])}.
    Please submit a Leave Application if applicable.</p>
    <p>Thank you.</p>
    """

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
        # Log an error if no email is found for the employee
        frappe.log_error(
            f"Email not found for employee {employee['employee_name']} ({employee['employee']})",
            "Absence Reminder"
        )
