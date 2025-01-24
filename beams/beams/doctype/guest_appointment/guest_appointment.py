# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class GuestAppointment(Document):
	def on_submit(self):
		self.validate_employee_availability()

	def validate_employee_availability(self):
	    '''
	    Validates if the employee associated with the document is available
	    on the specified appointment date.
		'''

	    if not self.received_by or not self.appointment_date:
	        frappe.throw("Recieved By and Appointment Date are mandatory.")

	    leave_applications = frappe.db.exists(
	        "Leave Application",
	        {
	            "employee": self.received_by,
	            "status": "Approved",
	            "from_date": ["<=", self.appointment_date],
	            "to_date": [">=", self.appointment_date],
	        }
	    )

	    if leave_applications:
	        frappe.throw(
	            f"The employee {self.received_by} has an approved leave on {self.appointment_date}."
	        )
