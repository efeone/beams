# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, nowtime
from frappe.utils.user import get_users_with_role
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils import today
from frappe import _


class InwardRegister(Document):
	def before_save(self):
		self.validate_posting_date()

	def on_submit(self, method=None):
	    """
	    Creates a ToDo task for the driver when the 'vehicle_key' checkbox is checked.
	    The notification message will be "Vehicle key handed over in Inward."
	    """
	    if self.vehicle_key:
	        driver_users = get_users_with_role("Driver")
	        if driver_users:
	            description = f"Vehicle key handed over in Inward for {self.visitor_name}."
	            if not frappe.db.exists('ToDo', {
	                'reference_name': self.name,
	                'reference_type': 'Inward Register',
	                'description': description
	            }):
	                add_assign({
	                    "assign_to": driver_users,
	                    "doctype": "Inward Register",
	                    "name": self.name,
	                    "description": description
	                })

	    if self.visitor_type == 'Courier':
	        courier_log = frappe.new_doc('Courier Log')
	        courier_log.courier_service = self.courier_service
	        courier_log.recipient = self.received_by
	        courier_log.description = self.purpose_of_visit
	        courier_log.insert()

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if self.posting_date > today():
				frappe.throw(_("Posting Date cannot be set after today's date."))
