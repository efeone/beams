# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AssetAuditing(Document):
    def before_submit(self):
        if len(self.asset_photos) < 3:
            frappe.msgprint(
                msg="Please upload atleast 3 photos before submission.",
                title="Message",
                indicator="red"
            )
            raise frappe.ValidationError
