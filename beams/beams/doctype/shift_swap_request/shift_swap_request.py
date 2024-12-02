# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, getdate
from frappe.model.document import Document

class ShiftSwapRequest(Document):
	def validate(self):
		# Validate future dates
		if getdate(self.shift_start_date) <= getdate(today()):
			frappe.throw("Shift Start Date must be a future date.")
		if getdate(self.shift_end_date) <= getdate(today()):
			frappe.throw("Shift End Date must be a future date.")

		# Validate shift assignments
		if not self.has_valid_shift_assignment():
			frappe.throw(f"Employee {self.employee} does not have a valid shift assignment in the given date range.")
		if not self.has_valid_shift_assignment(swap=1):
			frappe.throw(f"Swap With Employee {self.swap_with_employee} does not have a valid shift assignment in the given date range.")

		# Validate department
		employee_department = frappe.db.get_value("Employee", self.employee, "department")
		swap_employee_department = frappe.db.get_value("Employee", self.swap_with_employee, "department")

		if employee_department != swap_employee_department:
			frappe.throw(
				f"Employee {self.employee} and Swap With Employee {self.swap_with_employee} must belong to the same department."
			)

	def has_valid_shift_assignment(self, swap=0):
		"""
		Check if the given employee has a valid shift assignment within the specified date range.
		"""
		employee = self.employee if not swap else self.swap_with_employee
		return frappe.db.exists(
			"Shift Assignment",
			{
				"employee": employee,
				"start_date": ["<=", self.shift_end_date],
				"end_date": [">=", self.shift_start_date],
			}
		)
