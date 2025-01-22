# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe

class TechnicalRequest(Document):
    def on_cancel(self):
        # Validate that "Reason for Rejection" is filled if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")
