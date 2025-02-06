# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _
import json
from frappe.model.mapper import get_mapped_doc

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

@frappe.whitelist()
def map_award_record_to_travel_request(source_name, target_doc=None):
    """
    Map fields from Award Record DocType to Employee Travel Request DocType
    """

    def set_missing_values(source, target):
        target.requested_by = source.employee

    target_doc = get_mapped_doc(
        "Award Record",
        source_name,
        {
            "Award Record": {
                "doctype": "Employee Travel Request",
                "field_map": {"requested_by": "employee"},
            },
        },
        target_doc,
        set_missing_values,
    )

    if target_doc and source_name:
        target_doc.append(
            "dynamic_link",
            {
                "link_doctype": "Award Record",
                "link_name": source_name
            },
        )

    return target_doc
