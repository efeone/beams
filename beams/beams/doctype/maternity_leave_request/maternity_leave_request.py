# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days

class MaternityLeaveRequest(Document):

	def on_update(self):
		# Check if the workflow state is "Approved"
		if self.workflow_state == "Approved":
			# Fetch the Maternity Leave Type from HR Settings
			maternity_leave_type = frappe.db.get_single_value("Beams HR Settings", "maternity_leave_type")

			# Check if the Leave Type matches the Maternity Leave Type
			if self.leave_type == maternity_leave_type:
				self.create_leave_allocation()

	def create_leave_allocation(self):
		'''
		Create a Leave Allocation for the employee when a Maternity Leave Request is approved.
		'''
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

		frappe.msgprint(f"Leave Allocation created for {self.employee} ({self.leave_type}) from {self.from_date} to {to_date}.")
