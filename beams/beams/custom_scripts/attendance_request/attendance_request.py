import frappe
from frappe import _
from frappe.utils import format_date, get_link_to_form
from hrms.hr.doctype.attendance_request.attendance_request import AttendanceRequest
from hrms.hr.doctype.employee_checkin.employee_checkin import calculate_working_hours


class AttendanceRequestOverride(AttendanceRequest):
	def create_or_update_attendance(self, date: str):
		'''
			Method to Create or Update Attendance from Attendance Request
		'''
		attendance_name = self.get_attendance_record(date)
		status = self.get_attendance_status(date)

		if attendance_name:
			# Update existing attendance record
			doc = frappe.get_doc("Attendance", attendance_name)

			old_status = doc.status
			doc.db_set("attendance_request", self.name)

			if old_status != status:
				doc.db_set({"status": status})
				text = _("changed the status from {0} to {1} via Attendance Regularisation").format(
					frappe.bold(old_status), frappe.bold(status)
				)
				doc.add_comment(comment_type="Info", text=text)

				frappe.msgprint(
					_("Updated status from {0} to {1} for date {2} in the attendance record {3}").format(
						frappe.bold(old_status),
						frappe.bold(status),
						frappe.bold(format_date(date)),
						get_link_to_form("Attendance", doc.name),
					),
					title=_("Attendance Updated"),
				)
		else:
			# Create a new attendance record
			doc = frappe.new_doc("Attendance")
			doc.employee = self.employee
			doc.attendance_date = date
			doc.shift = self.shift
			doc.company = self.company
			doc.attendance_request = self.name
			doc.status = status
			doc.insert(ignore_permissions=True)
			doc.submit()










