# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class EmployeeAppraisalConsent(Document):
	def before_submit(self):
		self.validate_consent_conditions()

	def on_submit(self):
		self.update_appraisal_consent_status()	
		
	def validate_consent_conditions(self):
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

	def update_appraisal_consent_status(self):
		"""
		When employee submits the consent form,
		mark consent_received = 1 in the linked Appraisal.
		"""
		if self.appraisal:
			frappe.db.set_value("Appraisal", self.appraisal, "consent_received", 1)
			frappe.db.commit()		
