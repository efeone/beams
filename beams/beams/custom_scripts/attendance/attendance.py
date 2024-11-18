import frappe
from frappe.utils import nowdate, add_days

def send_absence_reminder():
    '''
    Send a reminder to the reports_to if an employee was absent but did not apply for leave.
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
            if not leave_exists:
                reports_to = frappe.db.get_value("Employee", employee["employee"], "reports_to")
                if reports_to:
                    reports_to_email = frappe.db.get_value("Employee", reports_to, "user_id")
                    if reports_to_email:
                        subject = f"Reminder:No Leave Application for Absent Employee"
                        message = f"""
                        <p>Dear {reports_to},</p>
                        <p>{employee['employee_name']} ({employee['employee']}) was absent on {employee['attendance_date']}
                        and has not submitted a leave application.</p>
                        <p>Please follow up with the {employee['employee_name']} and make a Necessary Action</p>
                        <p>Best regards,<br>HR Team</p>
                        """
                        frappe.sendmail(
                            recipients=reports_to_email,
                            subject=subject,
                            message=message
                        )
