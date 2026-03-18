# Copyright (c) 2026, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, get_last_day, getdate, nowdate

from beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet import _get_supplier_payable_account


class MonthlyConsolidatedTripSheet(Document):
	def validate(self):
		self._set_batta_totals_from_details()
		self._set_total_distance_and_fuel_from_details()
		self._validate_and_prepare_fuel_card_deduction()

	def on_update(self):
		self._apply_fuel_card_deduction()

	def on_trash(self):
		self._restore_fuel_card_on_delete()

	def _month_name_to_number(self, month_name):
		months = [
			"January", "February", "March", "April", "May", "June",
			"July", "August", "September", "October", "November", "December",
		]
		if month_name in months:
			return months.index(month_name) + 1
		return None

	def _set_batta_totals_from_details(self):
		"""Set total_batta, total_ot_batta, total_amount_received_driver; per-row and parent after-advance amounts."""
		total_batta = 0
		total_ot_batta = 0
		total_amount_received_driver = 0
		total_batta_after = 0
		total_ot_after = 0
		for row in self.get("monthly_consolidated_trip_sheet_details") or []:
			batta = flt(row.get("total_batta"))
			ot = flt(row.get("total_ot_batta"))
			advance = flt(row.get("amount_received_driver"))
			total_batta += batta
			total_ot_batta += ot
			total_amount_received_driver += advance
			# Advance applies to batta first, remainder to OT
			remaining_after_batta = max(0, advance - batta)
			batta_after = max(0, batta - advance)
			ot_after = max(0, ot - remaining_after_batta)
			row.total_batta_amount_after_advances = round(batta_after, 2)
			row.total_ot_amount_after_advances = round(ot_after, 2)
			total_batta_after += batta_after
			total_ot_after += ot_after
		self.total_batta = total_batta
		self.total_ot_batta = total_ot_batta
		self.total_amount_received_driver = total_amount_received_driver
		self.total_batta_amount_after_advances = round(total_batta_after, 2)
		self.total_ot_amount_after_advances = round(total_ot_after, 2)

	def _set_total_distance_and_fuel_from_details(self):
		"""Set total_distance_travelled, total_fuel_consumed and total_fuel_expense from child table rows."""
		total_distance = 0
		total_fuel = 0
		for row in self.get("monthly_consolidated_trip_sheet_details") or []:
			total_distance += flt(row.get("distance_travelledkm"))
			total_fuel += flt(row.get("fuel_consumption_l"))
		self.total_distance_travelled = total_distance
		self.total_fuel_consumed = total_fuel
		fuel_rate = flt(self.get("fuel_rate__litre"))
		self.total_fuel_expense = total_fuel * fuel_rate

	def _validate_and_prepare_fuel_card_deduction(self):
		"""Validate total_fuel_card_expense against bureau's fuel card limit; store old value for on_update."""
		expense = flt(self.get("total_fuel_card_expense"))
		if not self.bureau or expense <= 0:
			self._old_total_fuel_card_expense = 0
			return
		fuel_card_name = frappe.db.get_value("Bureau", self.bureau, "fuel_card")
		if not fuel_card_name:
			return
		old_expense = flt(
			frappe.db.get_value(self.doctype, self.name, "total_fuel_card_expense")
			if self.name else 0
		)
		self._old_total_fuel_card_expense = old_expense
		fuel_card = frappe.get_doc("Fuel Card", fuel_card_name)
		current_limit = flt(fuel_card.fuel_card_limit)
		# After we add back old deduction, available = current_limit + old_expense
		available = current_limit + old_expense
		if expense > available:
			frappe.throw(
				_("Total Fuel Card Expense ({0}) cannot exceed the bureau's Fuel Card available amount ({1}).").format(
					expense, available
				),
				title=_("Fuel Card Limit Exceeded"),
			)

	def _apply_fuel_card_deduction(self):
		"""Reduce the bureau's Fuel Card limit by total_fuel_card_expense (after adding back previous deduction)."""
		new_expense = flt(self.get("total_fuel_card_expense"))
		old_expense = getattr(self, "_old_total_fuel_card_expense", None)
		if old_expense is None and self.name:
			old_expense = flt(frappe.db.get_value(self.doctype, self.name, "total_fuel_card_expense"))
		if old_expense is None:
			old_expense = 0
		if not self.bureau:
			return
		fuel_card_name = frappe.db.get_value("Bureau", self.bureau, "fuel_card")
		if not fuel_card_name:
			return
		# No change
		if new_expense == old_expense:
			return
		fuel_card = frappe.get_doc("Fuel Card", fuel_card_name)
		current = flt(fuel_card.fuel_card_limit)
		# Add back what we had deducted before, then deduct new amount
		fuel_card.fuel_card_limit = current + old_expense - new_expense
		fuel_card.flags.ignore_permissions = True
		fuel_card.save(ignore_version=True)

	def _restore_fuel_card_on_delete(self):
		"""Restore total_fuel_card_expense to the bureau's Fuel Card when this doc is deleted."""
		expense = flt(self.get("total_fuel_card_expense"))
		if not self.bureau or expense <= 0:
			return
		fuel_card_name = frappe.db.get_value("Bureau", self.bureau, "fuel_card")
		if not fuel_card_name:
			return
		fuel_card = frappe.get_doc("Fuel Card", fuel_card_name)
		fuel_card.fuel_card_limit = flt(fuel_card.fuel_card_limit) + expense
		fuel_card.flags.ignore_permissions = True
		fuel_card.save(ignore_version=True)


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
def create_journal_entry(monthly_consolidated_trip_sheet_name):
	"""
	Create a Journal Entry for Monthly Consolidated Trip Sheet settlement.
	Uses accounts from Beams Accounts Settings (Bureau Trip Sheet Settings).

	Debit: Total Batta, Total OT, Total Fuel Expense (expenses).
	Credit: Total Fuel Card Expense (Fuel Log), Total Advance (amount received by driver).
	Balancing: Supplier Account (final settlement = Batta + OT + Fuel Expense - Fuel Log - Advance).
	"""
	doc = frappe.get_doc("Monthly Consolidated Trip Sheet", monthly_consolidated_trip_sheet_name)
	if not doc.supplier:
		frappe.throw(_("Supplier is not set on Monthly Consolidated Trip Sheet."))

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
	if not company:
		frappe.throw(_("Company could not be determined. Set Bureau or default Company."))

	settings = frappe.get_single("Beams Accounts Settings")
	batta_account = settings.get("batta_expense_item")
	fuel_expense_account = settings.get("fuel_expense_item")
	ot_account = settings.get("batta_ot_expense_item")
	fuel_card_account = settings.get("fuel_card_account")
	advance_account = settings.get("advance_account")

	supplier_payable_account = _get_supplier_payable_account(doc.supplier, company)
	if not supplier_payable_account:
		frappe.throw(
			_("No default payable account for Supplier {0} and Company {1}. Set it in Supplier or Company.").format(
				doc.supplier, company
			)
		)

	total_batta = round(flt(doc.total_batta), 2)
	total_ot = round(flt(doc.total_ot_batta), 2)
	total_fuel_expense = round(flt(doc.total_fuel_expense), 2)
	total_fuel_log = round(flt(doc.total_fuel_card_expense), 2)
	total_advance = round(flt(doc.total_amount_received_driver), 2)

	supplier_amount = round(total_batta + total_ot + total_fuel_expense - total_fuel_log - total_advance, 2)

	accounts = []
	if batta_account and total_batta:
		accounts.append({
			"account": batta_account,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": doc.total_batta_amount_after_advances,
		})
	if ot_account and total_ot:
		accounts.append({
			"account": ot_account,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": doc.total_ot_amount_after_advances,
		})
	if fuel_expense_account and total_fuel_expense:
		accounts.append({
			"account": fuel_expense_account,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": total_fuel_expense,
		})
	if fuel_card_account and total_fuel_log:
		accounts.append({
			"account": fuel_card_account,
			"debit_in_account_currency": total_fuel_log,
			"credit_in_account_currency": 0,
		})

	if supplier_payable_account and supplier_amount != 0:
		accounts.append({
			"account": supplier_payable_account,
			"party_type": "Supplier",
			"party": doc.supplier,
			"debit_in_account_currency": supplier_amount if supplier_amount > 0 else 0,
			"credit_in_account_currency": abs(supplier_amount) if supplier_amount < 0 else 0,
		})

	if not accounts:
		frappe.throw(_("No amounts to post. Set Batta, OT, Fuel Expense, Fuel Card or Advance, and ensure accounts are set in Beams Accounts Settings > Bureau Trip Sheet Settings."))

	je = frappe.new_doc("Journal Entry")
	je.voucher_type = "Journal Entry"
	je.posting_date = nowdate()
	je.company = company
	je.cost_center = cost_center or None
	je.user_remark = _("Settlement for Monthly Consolidated Trip Sheet {0} – {1}").format(doc.name, doc.supplier)

	for row in accounts:
		je.append("accounts", row)

	# requires party_type and party for Receivable/Payable accounts
	for d in je.get("accounts"):
		account_type = frappe.get_cached_value("Account", d.account, "account_type")
		if account_type in ("Receivable", "Payable") and not (d.party_type and d.party):
			d.party_type = "Supplier"
			d.party = doc.supplier

	je.flags.ignore_permissions = True
	je.insert()

	return je.name
