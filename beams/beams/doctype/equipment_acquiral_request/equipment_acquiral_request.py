# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe import _
from frappe.utils import today

class EquipmentAcquiralRequest(Document):
	def validate(self):
		self.validate_required_from_and_required_to()

	def before_save(self):
		self.validate_posting_date()

	def on_update_after_submit(self):
		if self.workflow_state == "Rejected" and not self.reason_for_rejection:
			frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

	@frappe.whitelist()
	def validate_required_from_and_required_to(self):
		"""
		Validates that required_from and required_to are properly set and checks
		if required_from is not later than required_to.
		"""
		if not self.required_from or not self.required_to:
			return
		required_from = getdate(self.required_from)
		required_to = getdate(self.required_to)

		if required_from > required_to:
			frappe.throw(
				msg=_('The "Required From" date cannot be after the "Required To" date.'),
				title=_('Validation Error')
			)


	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if getdate(self.posting_date) > getdate(today()):
				frappe.throw(_("Posting Date cannot be set after today's date."))
