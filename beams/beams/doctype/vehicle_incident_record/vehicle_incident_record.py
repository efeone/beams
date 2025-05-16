# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today
from frappe.utils import getdate



class VehicleIncidentRecord(Document):
    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))

    @frappe.whitelist()
    def validate_offense_date_and_time(self):
        if self.offense_date_and_time:
            offense_date = frappe.utils.getdate(self.offense_date_and_time)
            current_date = frappe.utils.getdate()

            if offense_date > current_date:
                frappe.throw(_("Offense Date cannot be in the future."))

            offense_date = frappe.utils.getdate(self.offense_date_and_time)  

            if self.trip_start_date and self.trip_end_date:
                start_date = frappe.utils.getdate(self.trip_start_date)
                end_date = frappe.utils.getdate(self.trip_end_date)

                if not (start_date <= offense_date <= end_date):
                    frappe.throw(_("Offense Date must be between Start Date and End Date of the trip."))
