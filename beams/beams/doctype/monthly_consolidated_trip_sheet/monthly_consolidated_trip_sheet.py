# Copyright (c) 2026, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, get_last_day, getdate
from frappe import _


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
		"""Set total_batta, total_ot_batta and total_amount_received_driver from sum of child table rows."""
		total_batta = 0
		total_ot_batta = 0
		total_amount_received_driver = 0
		for row in self.get("monthly_consolidated_trip_sheet_details") or []:
			total_batta += flt(row.get("total_batta"))
			total_ot_batta += flt(row.get("total_ot_batta"))
			total_amount_received_driver += flt(row.get("amount_received_driver"))
		self.total_batta = total_batta
		self.total_ot_batta = total_ot_batta
		self.total_amount_received_driver = total_amount_received_driver


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
		filters={"supplier": supplier, "bureau": bureau, "docstatus": 1},
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
		# Sum of settlement_journal_entries.amount for this Bureau Trip Sheet
		amount_received = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(amount), 0) FROM `tabBureau Trip Sheet Journal Entry`
			WHERE parent = %s
			""",
			(ts.get("name"),),
			as_dict=False,
		)
		amount_received_driver = flt(amount_received[0][0]) if amount_received else 0
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
			"amount_received_driver": amount_received_driver,
			"average_mileage_kmpl": ts.get("average_mileage_kmpl"),
			"fuel_consumption_l": ts.get("fuel_consumption_l"),
		})
	return rows


@frappe.whitelist()
def get_purchase_invoice_details(monthly_consolidated_trip_sheet_name):
	"""
	Get expense items from Beams Accounts Settings (Bureau Trip Sheet Settings) and
	rates from the Monthly Consolidated Trip Sheet for the Create Purchase Invoice popup.
	"""
	doc = frappe.get_doc("Monthly Consolidated Trip Sheet", monthly_consolidated_trip_sheet_name)
	company = None
	cost_center = None
	if doc.bureau:
		bureau_doc = frappe.db.get_value(
			"Bureau", doc.bureau, ["company", "cost_center"], as_dict=True
		)
		if bureau_doc:
			company = bureau_doc.get("company")
			cost_center = bureau_doc.get("cost_center")
	if not company:
		company = frappe.defaults.get_default("company")

	# Rent: Montly Rent (Driver) - Total amount Received (Driver), per Monthly Consolidated Trip Sheet
	rent_rate = flt(doc.total_montly_rent)

	# Order and labels match Beams Accounts Settings > Bureau Trip Sheet Settings tab
	# Read each item from Single doctype via db so values are always loaded
	item_specs = [
		("batta_expense_item", "Batta Expense Item", flt(doc.total_batta)),
		("fuel_expense_item", "Fuel Expense Item", flt(doc.total_fuel_expense)),
		("rent_expense_item", "Rent Expense Item", rent_rate),
		("batta_ot_expense_item", "Batta Ot Expense Item", flt(doc.total_ot_batta)),
	]
	items = []
	for field, label, rate in item_specs:
		item_code = frappe.db.get_single_value("Beams Accounts Settings", field)
		if not item_code:
			continue
		item_row = frappe.db.get_value(
			"Item", item_code, ["item_name", "stock_uom"], as_dict=True
		)
		item_name = (item_row and item_row.get("item_name")) or item_code
		uom = (item_row and item_row.get("stock_uom")) or "Nos"
		items.append({
			"item_code": item_code,
			"item_name": item_name,
			"uom": uom,
			"label": label,
			"rate": rate,
		})

	return {
		"supplier": doc.supplier,
		"bureau": doc.bureau,
		"company": company,
		"cost_center": cost_center,
		"posting_date": frappe.utils.nowdate(),
		"items": items,
	}


@frappe.whitelist()
def create_purchase_invoice_from_monthly_consolidated(monthly_consolidated_trip_sheet_name):
	"""
	Create a Purchase Invoice from Monthly Consolidated Trip Sheet using
	Beams Accounts Settings (Bureau Trip Sheet Settings) items and doc totals.
	"""
	details = get_purchase_invoice_details(monthly_consolidated_trip_sheet_name)
	if not details.get("supplier"):
		frappe.throw(_("Supplier is not set on Monthly Consolidated Trip Sheet."))
	if not details.get("items"):
		frappe.throw(_("No expense items configured in Beams Accounts Settings > Bureau Trip Sheet Settings."))

	pi = frappe.new_doc("Purchase Invoice")
	pi.supplier = details["supplier"]
	pi.bureau = details.get("bureau")
	pi.company = details.get("company") or frappe.defaults.get_default("company")
	pi.cost_center = details.get("cost_center")
	pi.set_posting_time = 1
	pi.posting_date = frappe.utils.nowdate()

	for row in details["items"]:
		if flt(row.get("rate")) == 0:
			continue
		pi.append("items", {
			"item_code": row["item_code"],
			"qty": 1,
			"rate": row["rate"],
		})

	pi.flags.ignore_permissions = True
	pi.insert()

	return pi.name
