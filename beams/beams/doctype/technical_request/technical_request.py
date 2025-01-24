# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe import _  # Import _ for translations


class TechnicalRequest(Document):
    def on_cancel(self):
        # Validate that "Reason for Rejection" is filled if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def validate(self):
        self.validate_required_from_and_required_to()

    @frappe.whitelist()
    def validate_required_from_and_required_to(self):
        """
        Validates that required_from and required_to are properly set and checks
        if required_from is not later than required_to.
        """
        if not self.required_from or not self.required_to:
            return
        # Convert dates to proper date objects
        required_from = getdate(self.required_from)
        required_to = getdate(self.required_to)

        if required_from > required_to:
            frappe.throw(
                msg=_("Required From cannot be after Required To."),
                title=_("Message")
            )
