# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _

class AssetTransferRequest(Document):
    def before_save(self):
        self.validate_posting_date()

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))
@frappe.whitelist()
def get_stock_items_from_bundle(bundle):
    # Fetch the stock items from the 'Asset Bundle Stock Item' table based on the 'bundle'
    stock_items = frappe.get_all('Asset Bundle Stock Item', filters={'parent': bundle}, fields=['item', 'uom', 'qty'])

    return stock_items
