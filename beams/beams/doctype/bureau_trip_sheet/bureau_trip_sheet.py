#  Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import math

from frappe.model.document import Document
from frappe.utils import flt, get_datetime, getdate, nowdate

import frappe
from frappe import _


class BureauTripSheet(Document):
	def validate(self):
		self.set_check_in_time()
		self.validate_odometer_readings()
		self.calculate_distance_from_odometer()
		self.calculate_total_distance_travelled()
		self.calculate_hours()
		self.calculate_daily_batta()
		self.calculate_batta()
		self.calculate_total_ot_batta()
		self.calculate_total_batta()
		self.calculate_total_daily_batta()
		self.validate_batta_policy()


	def set_check_in_time(self):
		"""
		Ensure single Check-In Time per day.
		Fetch from first created Trip Sheet of same date.
		"""
		if not self.starting_date_and_time:
			return

		current_date = getdate(self.starting_date_and_time)

		first_trip = frappe.db.get_value(
			"Bureau Trip Sheet",
			{
				"name": ["!=", self.name],
				"docstatus": ["!=", 2],
				"starting_date_and_time": ["between", [f"{current_date} 00:00:00", f"{current_date} 23:59:59"]]
			},
			"check_in_time",
			order_by="creation asc"
		)

		if first_trip:
			self.check_in_time = first_trip

	def calculate_batta(self):
		'''
		Calculate total trip batta from daily rate × number of days (or food allowance total).
		'''
		policy = get_batta_policy_values(supplier=self.supplier)

		if policy.get("is_actual_with") or policy.get("is_actual_without") or policy.get("is_actual_food"):

			self.total_food_allowance = (
				flt(self.breakfast) +
				flt(self.lunch) +
				flt(self.dinner)
			)

			self.batta = self.total_food_allowance

			return

		if self.total_food_allowance:
			self.batta = self.total_food_allowance
		else:
			number_of_days = max(1, math.ceil(flt(self.total_hours or 0) / 24))
			if self.is_overnight_stay:
				self.batta = number_of_days * flt(self.daily_batta_with_overnight_stay or 0)
			else:
				self.batta = number_of_days * flt(self.daily_batta_without_overnight_stay or 0)

	def calculate_total_distance_travelled(self):
		""" Calculate total distance travelled in km based on odometer readings or distance travelled field."""
		self.total_distance_travelled_km = flt(self.distance_travelledkm) or 0

	def validate_odometer_readings(self):
		""" Validate that odometer readings are non-negative and final reading is greater than initial reading. """
		initial = flt(self.initial_odometer_reading)
		final = flt(self.final_odometer_reading)
		if initial is not None and initial < 0:
			frappe.throw(_("Initial Odometer Reading cannot be negative."), title=_("Invalid Odometer Reading"))
		if final is not None and final < 0:
			frappe.throw(_("Final Odometer Reading cannot be negative."), title=_("Invalid Odometer Reading"))
		if initial is not None and final is not None and final <= initial:
			frappe.throw(
				_(f"Final Odometer Reading ({final}) must be greater than Initial ({initial})."),
				title=_("Invalid Odometer Reading")
			)

	def calculate_distance_from_odometer(self):
		""" Calculate distance travelled in km based on initial and final odometer readings, if both are provided."""
		if self.initial_odometer_reading is not None and self.final_odometer_reading is not None:
			self.distance_travelledkm = flt(self.final_odometer_reading) - flt(self.initial_odometer_reading)

	def calculate_hours(self):
		""" Calculate total hours based on Check-In Time and Ending Date/Time """

		start_time = self.check_in_time or self.starting_date_and_time

		if start_time and self.get("ending_date_and_time"):
			start = get_datetime(start_time)
			end = get_datetime(self.ending_date_and_time)

			if end > start:
				self.total_hours = round((end - start).total_seconds() / 3600.0, 2)
			else:
				self.total_hours = 0
		else:
			self.total_hours = 0

	def calculate_total_daily_batta(self):
		self.total_daily_batta = flt(self.batta) or 0

	def calculate_total_ot_batta(self):
		"""
		Calculate OT batta ONLY when last_trip is checked
		"""

		if not self.last_trip:
			self.total_ot_batta = 0
			return

		total_hours = flt(self.total_hours or 0)
		ot_rate = flt(self.ot_batta or 0)

		if not self.supplier or not total_hours:
			self.total_ot_batta = 0
			return

		ot_working_hours = flt(get_ot_working_hours(self.supplier) or 0)

		ot_hours = max(0, total_hours - ot_working_hours)

		self.total_ot_batta = round(ot_hours * ot_rate, 2)

	def calculate_daily_batta(self):
		'''
		Auto creation logic:
		✔ For Overnight Stay: BATTA (no food allowance) - always applies based on policy
		✔ For Normal (non-overnight):
		  - 100+ KM AND >= 8 Hours → BATTA (no food allowance)
		  - 50 to 100 KM AND >= 6 Hours → Food Allowance
		  - 100+ KM AND 6 to 8 Hours → Food Allowance
		  - Else → No Allowance
		When policy allows actual (editable) daily amounts, user-entered values are preserved on save.
		'''
		policy = get_batta_policy_values(supplier=self.supplier)

		if policy.get("is_actual_with") or policy.get("is_actual_without") or policy.get("is_actual_food"):
			return

		# Preserve manually entered daily rates before reset.
		manual_daily_batta_without_overnight = flt(self.get("daily_batta_without_overnight_stay"))
		manual_daily_batta_with_overnight = flt(self.get("daily_batta_with_overnight_stay"))
		has_manual_without_overnight = (not self.is_overnight_stay and manual_daily_batta_without_overnight > 0)
		has_manual_with_overnight = (self.is_overnight_stay and manual_daily_batta_with_overnight > 0)

		self.daily_batta_without_overnight_stay = 0
		self.daily_batta_with_overnight_stay = 0
		self.breakfast = 0
		self.lunch = 0
		self.dinner = 0
		self.total_food_allowance = 0
		self.batta = 0
		total_hours = flt(self.total_hours or 0)
		distance = flt(self.distance_travelledkm or self.total_distance_travelled_km or 0)
		number_of_days = max(1, math.ceil(total_hours / 24))
		if self.is_overnight_stay:
			batta_data = calculate_batta_allowance(
				designation="Driver",
				is_travelling_outside_kerala=self.is_travelling_outside_kerala or 0,
				is_overnight_stay=1,
				total_distance_travelled_km=distance,
				total_hours=total_hours
			)
			parent_daily_batta_value = flt(batta_data.get("daily_batta_with_overnight_stay", 0))
			if parent_daily_batta_value > 0:
				self.daily_batta_with_overnight_stay = parent_daily_batta_value
				self.batta = number_of_days * parent_daily_batta_value
		elif distance >= 100 and total_hours >= 8:
			batta_data = calculate_batta_allowance(
				designation="Driver",
				is_travelling_outside_kerala=self.is_travelling_outside_kerala or 0,
				is_overnight_stay=0,
				total_distance_travelled_km=distance,
				total_hours=total_hours
			)
			parent_daily_batta_value = flt(batta_data.get("daily_batta_without_overnight_stay", 0))
			if parent_daily_batta_value > 0:
				self.daily_batta_without_overnight_stay = parent_daily_batta_value
				self.batta = number_of_days * parent_daily_batta_value
		elif ((50 <= distance < 100 and total_hours >= 6) or (distance >= 100 and 6 <= total_hours < 8)):
			values = get_batta_for_food_allowance(
				designation="Driver",
				from_date_time=self.starting_date_and_time,
				to_date_time=self.ending_date_and_time,
				total_hrs=total_hours
			)
			self.breakfast = flt(values.get("break_fast", 0))
			self.lunch = flt(values.get("lunch", 0))
			self.dinner = flt(values.get("dinner", 0))
			self.total_food_allowance = self.breakfast + self.lunch + self.dinner
			self.batta = self.total_food_allowance

		# Re-apply manual rate after auto logic so save does not overwrite entered values.
		total_hours_for_manual_override = flt(self.total_hours or 0)
		number_of_days_for_manual_override = max(1, math.ceil(total_hours_for_manual_override / 24))
		if has_manual_without_overnight:
			self.daily_batta_without_overnight_stay = manual_daily_batta_without_overnight
			self.batta = number_of_days_for_manual_override * manual_daily_batta_without_overnight
			self.breakfast = 0
			self.lunch = 0
			self.dinner = 0
			self.total_food_allowance = 0
		if has_manual_with_overnight:
			self.daily_batta_with_overnight_stay = manual_daily_batta_with_overnight
			self.batta = number_of_days_for_manual_override * manual_daily_batta_with_overnight

	def calculate_total_batta(self):
		"""Calculate total driver batta on backend as daily + OT."""
		self.total_driver_batta = flt(self.total_daily_batta) + flt(self.total_ot_batta)

	def validate_batta_policy(self):
		'''
		Validate that a Driver Batta Policy exists for the supplier's designation.
		'''
		if not self.supplier:
			frappe.throw(title="Supplier Required", msg="Please select a Supplier before saving.")

		designation = frappe.db.get_value("Supplier", self.supplier, "designation")

		if not designation:
			frappe.throw(title="Designation Missing", msg=f"Designation not set for Supplier: {self.supplier}.")

		policy = frappe.db.exists(
			"Batta Policy",
			{"designation": designation}
		)

		if not policy:
			frappe.throw(
				title="Batta Policy Missing",
				msg=f"No Driver Batta Policy found for designation {designation}. Please create before saving."
			)

	def before_save(self):
		self.total_distance_travelled()

	def total_distance_travelled(self):
		""" Calculate total distance travelled in km based on initial and final odometer readings, if both are provided."""
		self.distance_travelledkm = flt(self.final_odometer_reading or 0) - flt(self.initial_odometer_reading or 0)


@frappe.whitelist()
def get_batta_for_food_allowance(designation, from_date_time, to_date_time, total_hrs):
	'''
		Method to get Batta for Food
	'''
	values = {'break_fast': 0, 'lunch': 0, 'dinner': 0}
	batta_policy = frappe.db.exists('Batta Policy', {'designation': designation})
	from_date_time = get_datetime(from_date_time)
	to_date_time = get_datetime(to_date_time)
	required_hours = 6

	if batta_policy and float(total_hrs) >= required_hours:
		break_fast, lunch, dinner = frappe.db.get_value('Batta Policy', batta_policy, ['break_fast', 'lunch', 'dinner'])
		same_date = getdate(from_date_time) == getdate(to_date_time)

		meal_times = {
			'break_fast': ('04:00', '09:00', break_fast),
			'lunch': ('12:30', '14:00', lunch),
			'dinner': ('18:00', '21:00', dinner)
		}

		for meal, (start_time, end_time, allowance) in meal_times.items():
			if same_date:
				date_threshold = getdate(from_date_time)
				if check_meal_time(from_date_time, to_date_time, date_threshold, start_time, end_time):
					values[meal] = allowance
			else:
				for date_threshold in [getdate(from_date_time), getdate(to_date_time)]:
					if check_meal_time(from_date_time, to_date_time, date_threshold, start_time, end_time):
						values[meal] += allowance

	return values

def check_meal_time(from_date_time, to_date_time, date_threshold, start_time, end_time):
	'''
		Check whether a meal time period (defined by `start_time` and `end_time`) falls within a given time range.
	'''
	start_datetime = get_datetime('{} {}'.format(date_threshold, start_time))
	end_datetime = get_datetime('{} {}'.format(date_threshold, end_time))
	return (from_date_time <= start_datetime <= to_date_time) or (from_date_time <= end_datetime <= to_date_time)

@frappe.whitelist()
def calculate_batta_allowance(designation=None, is_travelling_outside_kerala=0, is_overnight_stay=0, total_distance_travelled_km=0, total_hours=0):
	'''
		Calculation Of Total Batta Allowance based on Batta Policy
	'''
	def sanitize_number(value):
		try:
			return float(value)
		except:
			return 0
	total_distance_travelled_km = sanitize_number(total_distance_travelled_km)
	total_hours = sanitize_number(total_hours)

	batta_policy = frappe.get_all('Batta Policy', filters={'designation':designation}, fields=['*'])
	if not batta_policy:
		return {"batta": 0}

	policy = batta_policy[0]

	is_actual_daily_batta = policy.get('is_actual_') or 0
	is_actual_daily_batta_without_overnight = policy.get('is_actual__') or 0

	is_travelling_outside_kerala = bool(int(is_travelling_outside_kerala or 0))
	is_overnight_stay = bool(int(is_overnight_stay or 0))

	daily_batta_with_overnight_stay = 0
	daily_batta_without_overnight_stay = 0

	if not is_actual_daily_batta:
		if is_overnight_stay:
			if is_travelling_outside_kerala:
				daily_batta_with_overnight_stay = float(policy.get('outside_kerala__', 0))
			else:
				daily_batta_with_overnight_stay = float(policy.get('inside_kerala__', 0))

	if not is_actual_daily_batta_without_overnight:
		if not is_overnight_stay:
			if total_distance_travelled_km >= 100 and total_hours >= 8:
				if is_travelling_outside_kerala:
					daily_batta_without_overnight_stay = float(policy.get('outside_kerala', 0))
				else:
					daily_batta_without_overnight_stay = float(policy.get('inside_kerala', 0))

	return {
		"daily_batta_with_overnight_stay": daily_batta_with_overnight_stay,
		"daily_batta_without_overnight_stay": daily_batta_without_overnight_stay
	}

@frappe.whitelist()
def get_batta_policy_values(designation=None, supplier=None):
	'''
		Fetch and return the batta policy values from the 'Batta Policy' doctype
	'''
	if not designation and supplier:
		designation = frappe.db.get_value("Supplier", supplier, "designation")
	if not designation:
		return {}

	result = frappe.db.get_value(
		"Batta Policy",
		{"designation": designation},
		["is_actual_", "is_actual__", "is_actual___"],
		as_dict=True
	)

	if not result:
		return {}

	return {
		"is_actual_with":    int(result.get("is_actual_",   0) or 0),
		"is_actual_without": int(result.get("is_actual__",  0) or 0),
		"is_actual_food":    int(result.get("is_actual___", 0) or 0),
	}

@frappe.whitelist()
def get_ot_working_hours(supplier):
	"""
	Returns OT working hours based on Supplier or Beams Account Settings.
	If the supplier has a valid 'ot_working_hours', use that.
	Otherwise, fall back to 'default_working_hours' from Beams Accounts Settings.
	"""
	ot_hours = frappe.db.get_value("Supplier", supplier, "ot_working_hours")

	if not ot_hours:
		ot_hours = frappe.db.get_single_value("Beams Accounts Settings", "default_working_hours")

	return float(ot_hours or 0)


@frappe.whitelist()
def can_show_request_batta_button(bureau_trip_sheet):
	"""Return True if the current user's Employee is in the Bureau Trip Sheet's employees list."""
	bts = frappe.get_doc("Bureau Trip Sheet", bureau_trip_sheet)
	employee_names = [row.employee for row in (bts.employees or []) if row.get("employee")]
	if not employee_names:
		return False
	current_user_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	if not current_user_employee:
		return False
	return current_user_employee in employee_names


@frappe.whitelist()
def create_batta_claim(bureau_trip_sheet):
	"""  Create a Batta Claim based on the Bureau Trip Sheet details and return the claim document."""
	bts = frappe.get_doc("Bureau Trip Sheet", bureau_trip_sheet)
	
	claim = frappe.new_doc("Batta Claim")
	claim.employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	claim.bureau = bts.bureau
	claim.company = bts.company
	claim.purpose = bts.purpose
	claim.origin = bts.departure_location
	claim.destination = bts.destination_location
	claim.is_budgeted = bts.is_budgeted
	claim.is_travelling_outside_kerala = bts.is_travelling_outside_kerala
	claim.is_overnight_stay = bts.is_overnight_stay
	claim.append("work_detail", {
		"origin": bts.departure_location,
		"destination": bts.destination_location,
		"from_date_and_time": bts.starting_date_and_time,
		"to_date_and_time": bts.ending_date_and_time,
		"distance_travelled_km": bts.distance_travelledkm,
		"total_hours": bts.total_hours
	})

	return claim


@frappe.whitelist()
def get_supplier_payable_account(supplier=None, company=None):
	"""
	Get the supplier's default payable account for the given company.
	Looks up Supplier's accounts child table (Party Account or Accounts).
	Returns account name or empty string for use in UI.
	"""
	account = _get_supplier_payable_account(supplier, company)
	return account or ""


def _get_supplier_payable_account(supplier, company):
	"""
	Internal: get supplier default payable account for company.
	First from Party Account on Supplier; if not set, use ERPNext default
	(Supplier Group or Company default payable account).
	"""
	if not supplier or not company:
		return None
	# 1. Party Account on Supplier (company-specific account)
	account = frappe.db.get_value(
		"Party Account",
		{"parent": supplier, "parenttype": "Supplier", "company": company},
		"account",
	)
	if account:
		return account
	# 2. Fallback: ERPNext default (Supplier Group or Company default_payable_account)
	try:
		from erpnext.accounts.party import get_party_account
		account = get_party_account("Supplier", supplier, company)
		return account
	except Exception:
		return None


def get_mode_of_payment_account(mode_of_payment, company):
	"""Get the default account for the given Mode of Payment and company."""
	if not mode_of_payment or not company:
		return None
	return frappe.db.get_value(
		"Mode of Payment Account",
		{"parent": mode_of_payment, "parenttype": "Mode of Payment", "company": company},
		"default_account"
	)


@frappe.whitelist()
def create_settlement_journal_entry(bureau_trip_sheet, mode_of_payment, amount=None):
	"""
	Create a Journal Entry for: we have given (paid) the supplier the amount.
	- Debit: Supplier payable (our liability to supplier goes down)
	- Credit: Bank/Cash (money paid out to supplier)
	Supplier account is taken from Supplier doctype Default Accounts table.
	"""
	bts = frappe.get_doc("Bureau Trip Sheet", bureau_trip_sheet)
	if not bts.supplier:
		frappe.throw(_("Supplier is not set on this Bureau Trip Sheet."))
	company = bts.company or frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw(_("Company is not set on the Bureau Trip Sheet and no default Company found."))

	settlement_amount = flt(amount) if amount is not None else flt(bts.total_driver_batta)
	if settlement_amount <= 0:
		frappe.throw(_("Settlement amount must be greater than zero."))

	supplier_payable_account = _get_supplier_payable_account(bts.supplier, company)
	if not supplier_payable_account:
		frappe.throw(
			_("No default payable account found for Supplier {0} and Company {1}. Please set it in the Supplier's Accounting tab.").format(
				bts.supplier, company
			)
		)

	payment_account = get_mode_of_payment_account(mode_of_payment, company)
	if not payment_account:
		frappe.throw(
			_("No default account found for Mode of Payment {0} and Company {1}. Please configure it in Mode of Payment.").format(
				mode_of_payment, company
			)
		)

	journal_entry = frappe.new_doc("Journal Entry")
	journal_entry.voucher_type = "Journal Entry"
	journal_entry.posting_date = nowdate()
	journal_entry.company = company
	journal_entry.user_remark = _("Settlement for Bureau Trip Sheet {0} – Driver: {1}").format(
		bts.name, bts.supplier
	)
	if frappe.get_meta("Journal Entry").has_field("bureau_trip_sheet"):
		journal_entry.bureau_trip_sheet = bts.name

	# We have given the supplier the amount: Debit Supplier payable, Credit Bank/Cash
	journal_entry.append("accounts", {
		"account": supplier_payable_account,
		"party_type": "Supplier",
		"party": bts.supplier,
		"debit_in_account_currency": settlement_amount,
		"credit_in_account_currency": 0,
		"is_advance": "Yes"
	})
	journal_entry.append("accounts", {
		"account": payment_account,
		"debit_in_account_currency": 0,
		"credit_in_account_currency": settlement_amount,
		"is_advance": "Yes"
	})
	journal_entry.insert(ignore_permissions=True)

	return journal_entry.name

