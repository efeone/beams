# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime
from frappe import _


class OutwardRegister(Document):
    def before_save(self):
        self.validate_posting_date()

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if getdate(self.posting_date) > now_datetime().date():
                frappe.throw(_("Posting Date cannot be set after today's date."))
