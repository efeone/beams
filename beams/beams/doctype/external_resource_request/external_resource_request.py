# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate
from frappe import _

class ExternalResourceRequest(Document):

    def validate(self):
        self.validate_required_from_and_required_to()

    def before_save(self):
        self.validate_posting_date()

    @frappe.whitelist()
    def validate_required_from_and_required_to(self):
        """Validates required_from and required_to dates."""
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
            if self.posting_date > getdate(today()):
                frappe.throw(_("Posting Date cannot be set after today's date."))

    @frappe.whitelist()
    def updated_required_resources(self):
        for req in self.required_resources:
            req.required_from = self.required_from
            req.required_to = self.required_to
