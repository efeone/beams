# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime
from frappe import _  # Import _ for translation and localization

class TripSheet(Document):
    def validate(self):
        self.validate_start_datetime_and_end_datetime()

    @frappe.whitelist()
    def validate_start_datetime_and_end_datetime(self):
        """
        Validates that starting_datetime and ending_datetime are properly set and checks
        if starting_datetime is not later than ending_datetime.
        """
        if not self.starting_date_and_time or not self.ending_date_and_time:
            return

        # Convert datetimes to proper datetime objects
        starting_date_and_time = get_datetime(self.starting_date_and_time)
        ending_date_and_time = get_datetime(self.ending_date_and_time)

        if starting_date_and_time > ending_date_and_time:
            frappe.throw(
                msg=_("Starting Date and Time cannot be after Ending Date and Time."),
                title=_("Validation Error")
            )
@frappe.whitelist()
def get_last_odometer(vehicle):
    if not vehicle:
        return 0

    # Check if a Trip Sheet exists for the given vehicle
    last_trip_exists = frappe.db.exists(
        "Trip Sheet",
        {"vehicle": vehicle, "docstatus": 1},  # Only consider submitted Trip Sheets
    )

    if last_trip_exists:
        # Fetch the final_odometer of the last Trip Sheet
        final_odometer = frappe.db.get_value(
            "Trip Sheet",
            {"vehicle": vehicle, "docstatus": 1},
            "final_odometer_reading",
            order_by="creation desc",  # Ensure the latest trip sheet is fetched
        )
        return final_odometer or 0  # Return the final odometer or 0 if not found
    else:
        return 0  # Return 0 if no trip sheet exists for the vehicle
