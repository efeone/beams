# Copyright (c) 2026, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, getdate


class MonthlyConsolidatedTripSheet(Document):
	def after_insert(self):
		self.fetch_trip_sheets()

	def fetch_trip_sheets(self):
		"""Fetch Bureau Trip Sheets for the given supplier, bureau, month and year; add rows to child table."""
		if not all([self.supplier, self.bureau, self.month, self.year]):
			return
		month_number = self._month_name_to_number(self.month)
		if not month_number:
			return
		first_day = get_first_day(f"{self.year}-{month_number:02d}-01")
		last_day = get_last_day(first_day)
		trip_sheets = frappe.db.get_all(
			"Bureau Trip Sheet",
			filters={
				"supplier": self.supplier,
				"bureau": self.bureau,
			},
			fields=[
				"name", "departure_location", "destination_location",
				"initial_odometer_reading", "final_odometer_reading",
				"starting_date_and_time", "ending_date_and_time",
				"distance_travelledkm",
			],
		)
		self.monthly_consolidated_trip_sheet_details = []
		for ts in trip_sheets:
			start_date = ts.get("starting_date_and_time") and getdate(ts["starting_date_and_time"])
			if not start_date or not (first_day <= start_date <= last_day):
				continue
			self.append("monthly_consolidated_trip_sheet_details", {
				"departure_location": ts.get("departure_location") or "",
				"destination_location": ts.get("destination_location") or "",
				"initial_odometer_reading": ts.get("initial_odometer_reading"),
				"final_odometer_reading": ts.get("final_odometer_reading"),
				"starting_date_and_time": ts.get("starting_date_and_time"),
				"ending_date_and_time": ts.get("ending_date_and_time"),
				"distance_travelledkm": ts.get("distance_travelledkm"),
				"bureau_trip_sheet": ts.get("name")
			})
		if self.monthly_consolidated_trip_sheet_details:
			self.save()

	def _month_name_to_number(self, month_name):
		months = [
			"January", "February", "March", "April", "May", "June",
			"July", "August", "September", "October", "November", "December",
		]
		if month_name in months:
			return months.index(month_name) + 1
		return None
