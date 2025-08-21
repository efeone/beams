# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.form.assign_to import add as add_assign
from frappe.model.document import Document
from frappe.utils.user import get_users_with_role


class InwardRegister(Document):

	def before_save(self):
		self.validate_posting_date()

	def validate(self):
		if self.visitor_type == "Ex Employee":
			if not self.visitor_name or not self.visit_date:
				frappe.throw("Visitor Name and Visit Date are required for Ex Employees.")

			# Check if a Visit Request exists
			visit_request = frappe.db.exists(
				"Visit Request",
				{
					"visitor_name": self.visitor_name,
					"visit_date": self.visit_date
				}
			)
			if not visit_request:
				frappe.throw(f"No Visit Request found for {self.visitor_name} on {self.visit_date}.")

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if frappe.utils.get_datetime(self.posting_date) > frappe.utils.get_datetime():
				frappe.throw(_("Posting Date cannot be set after Now date."))
