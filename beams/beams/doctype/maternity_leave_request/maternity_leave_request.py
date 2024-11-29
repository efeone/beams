# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as add_assign, remove as remove_assign
from frappe.utils import add_days
from frappe.utils.user import get_users_with_role


class MaternityLeaveRequest(Document):

	def on_update(self):
		# Check if the workflow state is "Approved"
		if self.workflow_state == "Approved":
			self.create_leave_allocation()

		# Create ToDo for HOD when the request is created
		if self.workflow_state == "Pending HOD Approval":
			self.create_todo_for_hod()

		# Create ToDo for HR Manager when the request is in "Pending HR Approval"
		if self.workflow_state == "Pending HR Approval":
			self.remove_assignment_by_role("HOD")
			self.create_todo_for_hr_manager()

	def create_leave_allocation(self):
		"""
		Create a Leave Allocation for the employee when a Maternity Leave Request is approved.
		"""
		# Calculate the To Date as 365 days from the From Date
		to_date = add_days(self.from_date, 365)

		# Create Leave Allocation
		leave_allocation = frappe.get_doc({
			"doctype": "Leave Allocation",
			"employee": self.employee,
			"leave_type": self.leave_type,
			"from_date": self.from_date,
			"to_date": to_date,
			"new_leaves_allocated": self.no_of_days,
		})
		leave_allocation.insert(ignore_permissions=True)
		leave_allocation.submit()

		frappe.msgprint(
			f"Leave Allocation created for {self.employee} ({self.leave_type}) from {self.from_date} to {to_date}.",
			alert=True, indicator='green'
		)

	def create_todo_for_hod(self):
		"""
		Create a ToDo task for the HOD of the employee's department when a Maternity Leave Request is created.
		"""
		# Get the department of the employee
		department = frappe.db.get_value("Employee", self.employee, "department")

		if not department:
			frappe.msgprint(f"No department found for employee {self.employee}.", alert=True)
			return

		# Get the HOD's user ID from the department
		hod_user_id = frappe.db.get_value("Department", department, "head_of_department")
		hod_user = frappe.db.get_value("Employee", hod_user_id, "user_id")

		if not hod_user:
			frappe.msgprint(f"No Head of Department found for department {department}.", alert=True)
			return

		admin_message = f"A new Maternity Leave Request has been created for Employee {self.employee}. Please review it."
		add_assign({
			"assign_to": [hod_user],
			"doctype": "Maternity Leave Request",
			"name": self.name,
			"description": admin_message
		})

	def create_todo_for_hr_manager(self):
		"""
		Create a ToDo task for the HR Manager when the workflow state is "Pending HR Approval".
		"""
		hr_manager_users = get_users_with_role("HR Manager")

		if not hr_manager_users:
			frappe.msgprint("No HR Manager role user found.", alert=True)
			return

		admin_message = f"The Maternity Leave Request for Employee {self.employee} is pending HR approval. Please review it."
		add_assign({
			"assign_to": hr_manager_users,
			"doctype": "Maternity Leave Request",
			"name": self.name,
			"description": admin_message
		})

		frappe.msgprint("ToDo created for HR Manager.", alert=True)

	def remove_assignment_by_role(self, role):
		"""
		Removes ToDo assignments for users with a specific role for a given document.
		"""
		users = get_users_with_role(role)
		if users:
			for user in users:
				if frappe.db.exists('ToDo', {
					'reference_type': self.doctype,
					'reference_name': self.name,
					'allocated_to': user,
					'status': 'Open'
				}):
					remove_assign(
						doctype=self.doctype,
						name=self.name,
						assign_to=user
					)
					frappe.msgprint(f"Assignment for {user} removed.", alert=True)
