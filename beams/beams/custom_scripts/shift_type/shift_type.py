import frappe
import itertools
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, create_batch
from hrms.hr.doctype.shift_type.shift_type import ShiftType
from hrms.hr.doctype.employee_checkin.employee_checkin import skip_attendance_in_checkins, update_attendance_in_checkins, handle_attendance_exception

EMPLOYEE_CHUNK_SIZE = 50


class ShiftTypeOverride(ShiftType):
	@frappe.whitelist()
	def process_auto_attendance(self):
		if (
			not cint(self.enable_auto_attendance)
			or not self.process_attendance_after
			or not self.last_sync_of_checkin
		):
			return

		logs = self.get_employee_checkins()

		for key, group in itertools.groupby(logs, key=lambda x: (x["employee"], x["shift_start"])):
			single_shift_logs = list(group)
			attendance_date = key[1].date()
			employee = key[0]

			if not self.should_mark_attendance(employee, attendance_date):
				continue

			(
				attendance_status,
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
			) = self.get_attendance(single_shift_logs)

			mark_attendance_and_link_log(
				single_shift_logs,
				attendance_status,
				attendance_date,
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
				self.name,
			)

		# commit after processing checkin logs to avoid losing progress
		frappe.db.commit()  # nosemgrep

		assigned_employees = self.get_assigned_employees(self.process_attendance_after, True)

		# mark absent in batches & commit to avoid losing progress since this tries to process remaining attendance
		# right from "Process Attendance After" to "Last Sync of Checkin"
		for batch in create_batch(assigned_employees, EMPLOYEE_CHUNK_SIZE):
			for employee in batch:
				self.mark_absent_for_dates_with_no_attendance(employee)

			frappe.db.commit()  # nosemgrep


def mark_attendance_and_link_log(
	logs,
	attendance_status,
	attendance_date,
	working_hours=None,
	late_entry=False,
	early_exit=False,
	in_time=None,
	out_time=None,
	shift=None,
):
	"""Creates an attendance and links the attendance to the Employee Checkin.
	Note: If attendance is already present for the given date, the logs are marked as skipped and no exception is thrown.

	:param logs: The List of 'Employee Checkin'.
	:param attendance_status: Attendance status to be marked. One of: (Present, Absent, Half Day, Skip). Note: 'On Leave' is not supported by this function.
	:param attendance_date: Date of the attendance to be created.
	:param working_hours: (optional)Number of working hours for the given date.
	"""
	log_names = [x.name for x in logs]
	employee = logs[0].employee

	if attendance_status == "Skip":
		skip_attendance_in_checkins(log_names)
		return None

	elif attendance_status in ("Present", "Absent", "Half Day"):
		try:
			frappe.db.savepoint("attendance_creation")
			if frappe.db.exists("Attendance", { 'employee':employee, 'attendance_date':attendance_date }):
				# Checking whether there is attendance created, if yes then update the vlaues in it
				attendance_id = frappe.db.get_value("Attendance", { 'employee':employee, 'attendance_date':attendance_date })
				frappe.db.set_value('Attendance', attendance_id, 'working_hours', working_hours)
				frappe.db.set_value('Attendance', attendance_id, 'late_entry', late_entry)
				frappe.db.set_value('Attendance', attendance_id, 'early_exit', early_exit)
				frappe.db.set_value('Attendance', attendance_id, 'in_time', in_time)
				frappe.db.set_value('Attendance', attendance_id, 'out_time', out_time)
				attendance = frappe.get_doc("Attendance", attendance_id) 
			else:
				attendance = frappe.new_doc("Attendance")
				attendance.update(
					{
						"doctype": "Attendance",
						"employee": employee,
						"attendance_date": attendance_date,
						"status": attendance_status,
						"working_hours": working_hours,
						"shift": shift,
						"late_entry": late_entry,
						"early_exit": early_exit,
						"in_time": in_time,
						"out_time": out_time,
					}
				).submit()

				if attendance_status == "Absent":
					attendance.add_comment(
						text=_("Employee was marked Absent for not meeting the working hours threshold.")
					)

				update_attendance_in_checkins(log_names, attendance.name)
			return attendance

		except frappe.ValidationError as e:
			handle_attendance_exception(log_names, e)

	else:
		frappe.throw(_("{} is an invalid Attendance Status.").format(attendance_status))

