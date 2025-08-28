# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, getdate
from frappe.model.document import Document
from frappe.utils import add_days
from frappe.desk.form.assign_to import add as add_assign

class ShiftSwapRequest(Document):
	def validate(self):
		# Validate future dates
		if getdate(self.shift_start_date) <= getdate(today()):
			frappe.throw('Shift Start Date must be a future date.')
		if getdate(self.shift_end_date) <= getdate(today()):
			frappe.throw('Shift End Date must be a future date.')

		# Validate shift assignments
		if not self.has_valid_shift_assignment():
			employee_name = frappe.db.get_value('Employee', self.employee, 'employee_name')
			employee_link = f'<a href="/app/employee/{self.employee}" target="_blank">{employee_name}</a>'
			frappe.throw(f'Employee {employee_link} does not have a valid shift assignment in the given date range.')

		if not self.has_valid_shift_assignment(swap=1):
			swap_employee_name = frappe.db.get_value('Employee', self.swap_with_employee, 'employee_name')
			swap_employee_link = f'<a href="/app/employee/{self.swap_with_employee}" target="_blank">{swap_employee_name}</a>'
			frappe.throw(f'Swap With Employee {swap_employee_link} does not have a valid shift assignment in the given date range.')

		# Validate department
		employee_department = frappe.db.get_value('Employee', self.employee, 'department')
		swap_employee_department = frappe.db.get_value('Employee', self.swap_with_employee, 'department')

		if employee_department != swap_employee_department:
			# Fetch employee names
			employee_name = frappe.db.get_value('Employee', self.employee, 'employee_name')
			swap_employee_name = frappe.db.get_value('Employee', self.swap_with_employee, 'employee_name')

			employee_link = f'<a href="/app/employee/{self.employee}" target="_blank">{employee_name}</a>'
			swap_employee_link = f'<a href="/app/employee/{self.swap_with_employee}" target="_blank">{swap_employee_name}</a>'

			frappe.throw(
				f'Employee {employee_link} and Swap With Employee {swap_employee_link} must belong to the same department.',
				title="Department Mismatch"
			)


	def has_valid_shift_assignment(self, swap=0):
		'''
		Check if the given employee has a valid shift assignment within the specified date range.
		'''
		employee = self.employee if not swap else self.swap_with_employee
		return frappe.db.exists(
			'Shift Assignment',
			{
				'employee': employee,
				'start_date': ['<=', self.shift_end_date],
				'end_date': ['>=', self.shift_start_date],
			}
		)

	def on_update_after_submit(self):
		'''
		Triggered after the Shift Swap Request is updated.
		Initiates the shift swap if the workflow state is "Approved".
		'''
		if self.workflow_state == "Approved":
			self.swap_shifts()

	def swap_shifts(self):
		"""
		Swaps shifts between two employees while modifying existing shifts to adjust the swap period.
		Ensures shifts are properly split into new assignments without overlapping.
		Shift Type & Roster Type are also swapped.

		"""

		employee_shift = frappe.get_all(
			"Shift Assignment",
			filters={
				"employee": self.employee,
				"start_date": ["<=", self.shift_start_date],
				"end_date": [">=", self.shift_end_date],
				"docstatus": 1
			},
			fields=["name", "shift_type", "roster_type", "start_date", "end_date"]
		)

		swap_with_shift = frappe.get_all(
			"Shift Assignment",
			filters={
				"employee": self.swap_with_employee,
				"start_date": ["<=", self.shift_start_date],
				"end_date": [">=", self.shift_end_date],
				"docstatus": 1
			},
			fields=["name", "shift_type", "roster_type", "start_date", "end_date"]
		)

		shifts_to_submit = []

		# Case 1: Direct swap if both have the exact same date range
		if employee_shift and swap_with_shift:
			e_shift = employee_shift[0]
			s_shift = swap_with_shift[0]

			if e_shift["start_date"] == self.shift_start_date and e_shift["end_date"] == self.shift_end_date \
			   and s_shift["start_date"] == self.shift_start_date and s_shift["end_date"] == self.shift_end_date:

				frappe.db.set_value("Shift Assignment", e_shift["name"], {
					"shift_type": s_shift["shift_type"],
					"roster_type": s_shift["roster_type"]
				})
				frappe.db.set_value("Shift Assignment", s_shift["name"], {
					"shift_type": e_shift["shift_type"],
					"roster_type": e_shift["roster_type"]
				})
				frappe.msgprint(f"Shifts swapped  for the same date range between {self.employee} and {self.swap_with_employee}")
				return

		# Case 2: Partial overlaps → split and reassign
		def adjust_existing_shifts(shift_list, employee, swap_employee):
			"""
			Adjusts the existing shift assignments based on the swap period.
			Ensures the existing shift is modified and new shift assignments are created accordingly.
			Shift Type & Roster Type are swapped during reassignment.
			"""

			for shift in shift_list:
				shift_doc = frappe.get_doc("Shift Assignment", shift["name"])
				if shift_doc.employee == employee:
					# Get the shift type & roster type for the swap employee
					swap_shift_data = frappe.get_value(
						"Shift Assignment",
						{
							"employee": swap_employee,
							"start_date": shift["start_date"],
							"end_date": shift["end_date"]
						},
						["shift_type", "roster_type"],
					) or (shift["shift_type"], shift["roster_type"])  # Default to current values if none exist
					swap_shift_type, swap_roster_type = swap_shift_data

					if shift["start_date"] < self.shift_start_date and shift["end_date"] > self.shift_end_date:
						shift_doc.end_date = add_days(self.shift_start_date, -1)
						shift_doc.save()
						shifts_to_submit.append(create_shift(swap_employee, shift["shift_type"], shift["roster_type"], self.shift_start_date, self.shift_end_date))
						shifts_to_submit.append(create_shift(employee, shift["shift_type"], shift["roster_type"], add_days(self.shift_end_date, 1), shift["end_date"]))
					elif shift["start_date"] == self.shift_start_date and shift["end_date"] > self.shift_end_date:
						shift_doc.start_date = add_days(self.shift_end_date, 1)
						shift_doc.save()
						shifts_to_submit.append(create_shift(swap_employee, shift["shift_type"], shift["roster_type"], self.shift_start_date, self.shift_end_date))
					elif shift["start_date"] < self.shift_start_date and shift["end_date"] == self.shift_end_date:
						shift_doc.end_date = add_days(self.shift_start_date, -1)
						shift_doc.save()

						shifts_to_submit.append(create_shift(swap_employee, shift["shift_type"], shift["roster_type"], self.shift_start_date, self.shift_end_date))
				elif shift_doc.employee == swap_employee:
					# Get the shift type & roster type for the swap employee
					swap_shift_data = frappe.get_value(
						"Shift Assignment",
						{
							"employee": employee,
							"start_date": shift["start_date"],
							"end_date": shift["end_date"]
						},
						["shift_type", "roster_type"],
					) or (shift["shift_type"], shift["roster_type"])  # Default to current values if none exist
					swap_shift_type, swap_roster_type = swap_shift_data

					if shift["start_date"] < self.shift_start_date and shift["end_date"] > self.shift_end_date:
						shift_doc.end_date = add_days(self.shift_start_date, -1)
						shift_doc.save()
						shifts_to_submit.append(create_shift(employee, shift["shift_type"], shift["roster_type"], self.shift_start_date, self.shift_end_date))
						shifts_to_submit.append(create_shift(swap_employee, shift["shift_type"], shift["roster_type"], add_days(self.shift_end_date, 1), shift["end_date"]))
					elif shift["start_date"] == self.shift_start_date and shift["end_date"] > self.shift_end_date:
						shift_doc.start_date = add_days(self.shift_end_date, 1)
						shift_doc.save()
						shifts_to_submit.append(create_shift(employee, shift["shift_type"], shift["roster_type"], self.shift_start_date, self.shift_end_date))
					elif shift["start_date"] < self.shift_start_date and shift["end_date"] == self.shift_end_date:
						shift_doc.end_date = add_days(self.shift_start_date, -1)
						shift_doc.save()

						shifts_to_submit.append(create_shift(employee, shift["shift_type"], shift["roster_type"], self.shift_start_date, self.shift_end_date))


		def create_shift(employee, shift_type, roster_type, start_date, end_date):
			"""
			Creates a new shift assignment for the given period.
			Ensures Shift Type & Roster Type are swapped accordingly.
			"""
			new_shift = frappe.new_doc("Shift Assignment")
			new_shift.update({
				"employee": employee,
				"shift_type": shift_type,
				"roster_type": roster_type,
				"start_date": start_date,
				"end_date": end_date,
				"status": "Active"
			})
			return new_shift

		# Adjust shifts for both employees
		adjust_existing_shifts(employee_shift, self.employee, self.swap_with_employee)
		adjust_existing_shifts(swap_with_shift, self.swap_with_employee, self.employee)

		for s_shift in shifts_to_submit:
			s_shift.insert(ignore_permissions=True)
			s_shift.submit()

def get_permission_query_conditions(user):
	'''
	Permission query conditions for Shift Swap Request based on user roles.
	- System Manager and HR Manager have unrestricted access.
	- HOD can access requests within their department.
	- Employees can access their own requests and those where they are the swap_with_employee.
	'''
	if not user: 
		user = frappe.session.user
	
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "HR Manager" in user_roles or "CEO" in user_roles:
		return None
	
	if "HOD" in user_roles:
		department = frappe.db.get_value("Employee", {"user_id": user}, "department")
		if department:
			return f"`tabShift Swap Request`.department = '{department}'"

	if "Employee" in user_roles:
		employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if employee:
			return f"""(`tabShift Swap Request`.employee = '{employee}' 
					 OR `tabShift Swap Request`.swap_with_employee = '{employee}')"""
