# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _

class AssetAuditing(Document):
    def before_save(self):
        self.validate_posting_date()
        
    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))

    def before_submit(self):
        if len(self.asset_photos) < 3:
            frappe.msgprint(
                msg="Please upload atleast 3 photos before submission.",
                title="Message",
                indicator="red"
            )
            raise frappe.ValidationError
