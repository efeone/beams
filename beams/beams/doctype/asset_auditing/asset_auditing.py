# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _

class AssetAuditing(Document):

    def before_save(self):
        self.validate_posting_date()
    
    def before_submit(self):
        self.validate_image_attached()
    
    def validate_image_attached(self):
        """ 
        Ensure each row in asset_auditing_detail has exactly 3 images attached.
        """
        for idx, row in enumerate(self.asset_auditing_detail, start=1):
            images = [row.image, row.image_2, row.image_3]
            attached_images = [img for img in images if img]
            if len(attached_images) != 3:
                frappe.throw(f"Row {idx} must have exactly 3 images attached.")
    
    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date and self.posting_date > today():
            frappe.throw(_("Posting Date cannot be set after today's date."))
