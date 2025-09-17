# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeAppraisalConsent(Document):
	


	def before_submit(self):
		"""
		Validate conditions before submitting the document:
		1. Ensure 'Consent Given' checkbox is checked.
		2. Ensure 'Employee Signature' field is filled.
		3. Ensure that only the selected employee can submit this document.
		"""
		if not self.consent_given:
			frappe.throw(_("You must check 'Consent Given' before submitting."))
		employee_user_id = frappe.db.get_value("Employee", self.employee, "user_id")
		if frappe.session.user != employee_user_id:
			frappe.throw(_("Only the selected employee can submit this document."))
