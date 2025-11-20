#  Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
import math
from frappe.model.document import Document
from frappe.utils import get_datetime, getdate, flt
from frappe import _
from frappe.utils import nowdate


class BureauTripSheet(Document):
	def validate(self):
		self.calculate_total_distance_travelled()
		self.calculate_hours()
		self.calculate_daily_batta()
		self.calculate_batta()
		self.calculate_total_ot_batta()
		self.calculate_total_batta()
		self.calculate_total_daily_batta()
		self.calculate_total_distance_based_on_odometer()
		self.validate_batta_policy()

	def calculate_batta(self):
		'''
		Calculate the total batta (allowance) based on daily batta amounts.
		'''
		self.batta = (self.daily_batta_without_overnight_stay or 0) \
				   + (self.daily_batta_with_overnight_stay or 0)

	def calculate_total_distance_travelled(self):
		'''
		Calculate the total distance travelled by summing up the
		distance_travelled_km' values from work details.
		'''
		total_distance = 0

		if self.work_details:
			for row in self.work_details:
				if row.distance_travelled_km:
					total_distance += row.distance_travelled_km

		self.total_distance_travelled_km = total_distance

	@frappe.whitelist()
	def calculate_total_distance_based_on_odometer(self):
		'''
		Validate odometer readings and calculate distance travelled.
		Automatically updates the fields on the same document.
		'''
		if self.final_odometer_reading is None or self.initial_odometer_reading is None:
			return

		if self.initial_odometer_reading > self.final_odometer_reading:
			frappe.throw(_("Initial Odometer Reading must be less than Final Odometer Reading"))

		self.total_distance_km = self.final_odometer_reading - self.initial_odometer_reading
		return self.total_distance_km

	def calculate_hours(self):
		'''
		Calculate the total hours worked by summing up the 'total_hours' values from work details.
		'''
		total_hours = 0

		if self.work_details:
			for row in self.work_details:
				if row.total_hours:
					total_hours += float(row.total_hours)

		self.total_hours = total_hours

	def calculate_total_daily_batta(self):
		'''
		Calculate the total daily batta by summing up the 'total_batta' values from work details.
		'''
		total_batta = 0

		if self.work_details:
			for row in self.work_details:
				if row.total_batta:
					total_batta += row.total_batta

		self.total_daily_batta = total_batta

	def calculate_total_ot_batta(self):
		'''
		Calculate the total OT batta by summing up the 'ot_batta' values from work details.
		'''
		total_ot_batta = 0

		if self.work_details:
			for row in self.work_details:
				if row.ot_batta:
					total_ot_batta += row.ot_batta

		self.total_ot_batta = total_ot_batta

	def calculate_daily_batta(self):
		'''
		Auto creation logic:
		✔ For Overnight Stay: BATTA (no food allowance) - always applies based on policy
		✔ For Normal (non-overnight):
		  - 100+ KM AND >= 8 Hours → BATTA (no food allowance)
		  - 50 to 100 KM AND >= 6 Hours → Food Allowance
		  - 100+ KM AND 6 to 8 Hours → Food Allowance
		  - Else → No Allowance
		'''
		self.daily_batta_without_overnight_stay = 0
		self.daily_batta_with_overnight_stay = 0
		if not self.get("work_details"):
			return
		for row in self.work_details:
			total_hours = flt(row.total_hours or 0)
			distance = flt(row.distance_travelled_km or 0)
			row.number_of_days = max(1, math.ceil(total_hours / 24))
			row.daily_batta = 0
			row.breakfast = 0
			row.lunch = 0
			row.dinner = 0
			row.total_food_allowance = 0
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
					row.daily_batta = row.number_of_days * parent_daily_batta_value
				continue
			if distance >= 100 and total_hours >= 8:
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
					row.daily_batta = row.number_of_days * parent_daily_batta_value
				continue
			elif ((50 <= distance < 100 and total_hours >= 6) or
				  (distance >= 100 and 6 <= total_hours < 8)):
				values = get_batta_for_food_allowance(
					designation="Driver",
					from_date_time=row.from_date_and_time,
					to_date_time=row.to_date_and_time,
					total_hrs=total_hours
				)
				row.breakfast = values.get("break_fast", 0)
				row.lunch = values.get("lunch", 0)
				row.dinner = values.get("dinner", 0)
				row.total_food_allowance = flt(row.breakfast) + flt(row.lunch) + flt(row.dinner)
				continue

	def calculate_total_batta(self):
		'''
		Server-side equivalent of JS calculate_total_batta.
		Calculates total_batta = daily_batta + total_food_allowance for each row.
		'''
		if not self.get('work_details'):
			return

		for row in self.work_details:
			daily_batta = row.daily_batta or 0
			food_allowance = row.total_food_allowance or 0
			row.total_batta = daily_batta + food_allowance

	def on_submit(self):
		'''
			Create a Purchase Invoice on submission of Bureau Trip Sheet
		'''
		if not self.supplier:
			frappe.throw(_("Please select a Supplier to create a Purchase Invoice."))

		service_item = frappe.db.get_single_value("Beams Accounts Settings", "default_trip_sheet_service_item")
		if not service_item:
			frappe.throw(_("Please configure the Default Trip Sheet Service Item in Beams Accounts Settings."))

		if not self.purchase_invoice:
			pi = frappe.new_doc("Purchase Invoice")
			pi.supplier = self.supplier
			pi.company = self.company
			pi.set_posting_time = 1
			pi.posting_date = nowdate()
			pi.append("items", {
				"item_code": service_item,
				"qty": 1,
				"rate": self.total_driver_batta,
				"amount": self.total_driver_batta
			})
			pi.flags.ignore_permissions = True
			pi.insert()
			pi.submit()
			frappe.msgprint(
				_('Purchase Invoice Created: <a href="{0}">{1}</a>').format(
					frappe.utils.get_url_to_form("Purchase Invoice", pi.name),
					pi.name
				),
				alert=True,
				indicator='green'
			)
			self.db_set("purchase_invoice", pi.name)

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

	if batta_policy and float(total_hrs) > required_hours:
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

	batta_policy = frappe.get_all('Batta Policy', filters={'designation':'Driver'}, fields=['*'])
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
			if total_distance_travelled_km > 100 and total_hours >= 8:
				if is_travelling_outside_kerala:
					daily_batta_without_overnight_stay = float(policy.get('outside_kerala', 0))
				else:
					daily_batta_without_overnight_stay = float(policy.get('inside_kerala', 0))

	return {
		"daily_batta_with_overnight_stay": daily_batta_with_overnight_stay,
		"daily_batta_without_overnight_stay": daily_batta_without_overnight_stay
	}

@frappe.whitelist()
def get_batta_policy_values():
	'''
		Fetch and return the batta policy values from the 'Batta Policy' doctype
	'''
	result = frappe.db.get_value('Batta Policy', {}, ['is_actual', 'is_actual_', 'is_actual__', 'is_actual___'], as_dict=True)
	return result

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