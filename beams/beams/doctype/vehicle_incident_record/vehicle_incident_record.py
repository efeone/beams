# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _

class VehicleIncidentRecord(Document):
    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))

    @frappe.whitelist()
    def validate_offense_date_and_time(self):
        if self.offense_date_and_time:
            if self.offense_date_and_time > today():
                frappe.throw(_("Offense Date cannot be set after today's date."))
