# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AwardRecord(Document):
    def validate(self):
        self.update_total_amount()

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
