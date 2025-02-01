# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _

class VehicleHireRequest(Document):
    def on_submit(self):
        self.update_hired_vehicles_on_submit()

    def on_cancel(self):
        self.update_hired_vehicles_on_cancel()

    def before_save(self):
        self.validate_posting_date()

    def update_hired_vehicles_on_submit(self):
        '''
        Calculate the total number of vehicles from the required_vehicles child table
        and update the linked Transportation Request.
        '''
        if self.required_vehicles:
            # Calculate the total number of vehicles
            total_vehicles = sum(row.no_of_vehicles or 0 for row in self.required_vehicles)

            # Update the Transportation Request
            if self.transportation_request:
                frappe.db.set_value(
                    "Transportation Request",
                    self.transportation_request,
                    "no_of_hired_vehicles",
                    total_vehicles
                )

    def update_hired_vehicles_on_cancel(self):
        '''
        On  cancellation of Transportation Request reset the number of hired vehicles

		'''
        if self.transportation_request:
            frappe.db.set_value(
                "Transportation Request",
                self.transportation_request,
                "no_of_hired_vehicles",
                0
            )

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))
