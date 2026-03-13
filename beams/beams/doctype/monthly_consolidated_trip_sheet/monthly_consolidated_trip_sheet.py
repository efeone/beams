# Copyright (c) 2026, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, get_last_day, getdate


class MonthlyConsolidatedTripSheet(Document):
	def validate(self):
		self._set_batta_totals_from_details()

	def _month_name_to_number(self, month_name):
		months = [
			"January", "February", "March", "April", "May", "June",
			"July", "August", "September", "October", "November", "December",
		]
		if month_name in months:
			return months.index(month_name) + 1
		return None

	def _set_batta_totals_from_details(self):
		"""Set total_batta and total_ot_batta from sum of child table rows."""
		total_batta = 0
		total_ot_batta = 0
		for row in self.get("monthly_consolidated_trip_sheet_details") or []:
			total_batta += flt(row.get("total_batta"))
			total_ot_batta += flt(row.get("total_ot_batta"))
		self.total_batta = total_batta
		self.total_ot_batta = total_ot_batta


@frappe.whitelist()
def fetch_trip_sheets(supplier, bureau, month, year):
	"""
	Fetch Bureau Trip Sheets for the given supplier, bureau, month and year.
	Returns a list of row dicts for the child table (monthly_consolidated_trip_sheet_details).
	"""
	if not all([supplier, bureau, month, year]):
		return []
	months = [
		"January", "February", "March", "April", "May", "June",
		"July", "August", "September", "October", "November", "December",
	]
	month_number = months.index(month) + 1 if month in months else None
	if not month_number:
		return []
	first_day = get_first_day(f"{year}-{month_number:02d}-01")
	last_day = get_last_day(first_day)
	trip_sheets = frappe.db.get_all(
		"Bureau Trip Sheet",
		filters={"supplier": supplier, "bureau": bureau},
		fields=[
			"name", "departure_location", "destination_location",
			"initial_odometer_reading", "final_odometer_reading",
			"starting_date_and_time", "ending_date_and_time",
			"distance_travelledkm", "total_daily_batta", "total_ot_batta",
			"average_mileage_kmpl", "fuel_consumption_l",
		],
	)
	rows = []
	for ts in trip_sheets:
		start_date = ts.get("starting_date_and_time") and getdate(ts["starting_date_and_time"])
		if not start_date or not (first_day <= start_date <= last_day):
			continue
		rows.append({
			"departure_location": ts.get("departure_location") or "",
			"destination_location": ts.get("destination_location") or "",
			"initial_odometer_reading": ts.get("initial_odometer_reading"),
			"final_odometer_reading": ts.get("final_odometer_reading"),
			"starting_date_and_time": ts.get("starting_date_and_time"),
			"ending_date_and_time": ts.get("ending_date_and_time"),
			"distance_travelledkm": ts.get("distance_travelledkm"),
			"bureau_trip_sheet": ts.get("name"),
			"total_batta": ts.get("total_daily_batta"),
			"total_ot_batta": ts.get("total_ot_batta"),
			"average_mileage_kmpl": ts.get("average_mileage_kmpl"),
			"fuel_consumption_l": ts.get("fuel_consumption_l"),
		})
	return rows
