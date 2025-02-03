# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _ 

class AwardRecord(Document):
    def before_save(self):
        self.update_total_amount()
        self.validate_posting_date()

    @frappe.whitelist()
    def update_total_amount(self):
        # Initialize total amount
        total_amount = 0

        # Sum up the Amount from the child table 'expenses'
        if self.expenses:
            for expense in self.expenses:
                total_amount += expense.amount

        # Set the Total Amount field
        self.total_amount = total_amount

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))
