import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime
from frappe import _  # Import _ for translation and localization

class TripSheet(Document):
    def validate(self):
        self.validate_start_datetime_and_end_datetime()
        self.calculate_and_validate_fuel_data()

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
    def calculate_and_validate_fuel_data(self):
        """
        Validate odometer readings and calculate distance traveled and fuel consumption per km.
        Automatically updates the fields on the same document.
        """
        # Validate odometer readings
        if self.initial_odometer_reading > self.final_odometer_reading:
            frappe.throw(_("Initial Odometer Reading must be less than  Final Odometer Reading"))

        # Calculate distance traveled
        if self.final_odometer_reading and self.initial_odometer_reading:
            self.distance_traveledkm = self.final_odometer_reading - self.initial_odometer_reading
        else:
            self.distance_traveledkm = 0

        # Calculate fuel consumption per km
        if self.fuel_consumed and self.fuel_consumed != 0 and self.distance_traveledkm:
            self.fuel_consumption_per_km = self.distance_traveledkm / self.fuel_consumed
        else:
            self.fuel_consumption_per_km = 0



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
