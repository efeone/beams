import frappe
from frappe import _
from frappe.utils import format_date, get_link_to_form
from hrms.hr.doctype.attendance_request.attendance_request import AttendanceRequest


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
			checkin_time, checkout_time = get_checkin_checkout_time(doc.employee, doc.attendance_date)
			if not doc.in_time and checkin_time:
				doc.db_set("in_time", checkin_time)
			if not doc.out_time and checkout_time:
				doc.db_set("out_time", checkout_time)

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

def get_checkin_checkout_time(employee, attendance_date):
	'''
		Method to get First Checkin and Last Checkout Time based on attednace date and employee
	'''
	checkin_time, checkout_time = None, None
	if frappe.db.exists('Attendance', { 'attendance_date':attendance_date, 'employee':employee }):
		attendance_doc = frappe.get_doc('Attendance', { 'attendance_date':attendance_date, 'employee':employee })
		if attendance_doc.in_time and not attendance_doc.out_time:
			checkin_record = frappe.db.get_value('Employee Checkin', { 'attendance':attendance_doc.name, 'time':attendance_doc.in_time })
			checkout_time = get_checkout_time(employee, checkin_record)
		if attendance_doc.out_time and not attendance_doc.in_time:
			checkout_record = frappe.db.get_value('Employee Checkin', { 'attendance':attendance_doc.name, 'time':attendance_doc.out_time })
			checkin_time = get_checkin_time(employee, checkout_record)
	return checkin_time, checkout_time

def get_checkout_time(employee, checkin_record):
	'''
		Fetches the last checkout time for an employee after the provided checkin record.
	'''
	checkout_time = None
	if frappe.db.exists('Employee Checkin', checkin_record):
		checkin_time = frappe.db.get_value('Employee Checkin', checkin_record, 'time')
		checkins = frappe.get_all(
			"Employee Checkin",
			fields=[
				"name",
				"employee",
				"log_type",
				"time",
				"shift",
				"shift_start",
				"shift_end",
				"shift_actual_start",
				"shift_actual_end"
			],
			filters={
				"skip_auto_attendance": 0,
				"employee": employee,
				"attendance": ("is", "not set"),
				"time": (">=", checkin_time)
			},
			order_by="time",
		)
		for checkin in checkins:
			if checkin.log_type == 'OUT' and not checkin.shift:
				checkout_time = checkin.time
			if checkout_time and checkin.shift:
				return checkout_time
	return checkout_time

def get_checkin_time(employee, checkout_record):
	'''
		 Fetches the first check-in time for an employee before the provided checkout record.
	'''
	checkin_time = None
	if frappe.db.exists('Employee Checkin', checkout_record):
		checkout_time = frappe.db.get_value('Employee Checkin', checkout_record, 'time')
		checkins = frappe.get_all(
			"Employee Checkin",
			fields=[
				"name",
				"employee",
				"log_type",
				"time",
				"shift",
				"shift_start",
				"shift_end",
				"shift_actual_start",
				"shift_actual_end"
			],
			filters={
				"skip_auto_attendance": 0,
				"employee": employee,
				"attendance": ("is", "not set"),
				"time": ("<=", checkout_time)
			},
			order_by="time desc",
		)
		for checkin in checkins:
			if checkin.log_type == 'IN' and not checkin.shift:
				checkin_time = checkin.time
			if checkin_time and checkin.shift:
				return checkin_time
	return checkin_time







