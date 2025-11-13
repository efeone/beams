#  Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, getdate
from frappe import _
from frappe.utils import nowdate


class BureauTripSheet(Document):
	def validate(self):
		self.calculate_batta()
		self.calculate_total_distance_travelled()
		self.calculate_hours()
		self.calculate_total_daily_batta()
		self.calculate_total_ot_batta()
		self.calculate_total_distance_based_on_odometer()

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
		"""
		Calculate the total OT batta by summing up the 'ot_batta' values from work details.
		"""
		total_ot_batta = 0

		if self.work_details:
			for row in self.work_details:
				if row.ot_batta:
					total_ot_batta += row.ot_batta

		self.total_ot_batta = total_ot_batta

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


@frappe.whitelist()
def get_batta_for_food_allowance(designation, from_date_time, to_date_time, total_hrs, distance_travelled_km=0):
	'''
		Method to get Batta for Food
	'''
	values = {'break_fast': 0, 'lunch': 0, 'dinner': 0}
	batta_policy = frappe.db.exists('Batta Policy', {'designation': designation})
	from_date_time = get_datetime(from_date_time)
	to_date_time = get_datetime(to_date_time)
	required_hours = 6
	distance = float(distance_travelled_km or 0)

	if batta_policy and float(total_hrs) > required_hours and 50 < distance <= 100:
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

	batta_policy = frappe.get_all('Batta Policy', filters={'designation': 'Driver'}, fields=['*'])
	if not batta_policy:
		frappe.throw(f"No Batta Policy found for the designation: {designation}")
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

    # Check for None, 0, or empty string
    if not ot_hours:
        ot_hours = frappe.db.get_single_value("Beams Accounts Settings", "default_working_hours")

    # Return a numeric value (float for better accuracy)
    return float(ot_hours or 0)

@frappe.whitelist()
def get_allowances(designation, distance_travelled_km, total_hours, from_date_time, to_date_time, is_overnight_stay=0, is_travelling_outside_kerala=0):
    """
    Decide which allowance applies:
    - Overnight stay → Travel Batta
    - >100 km & >=8 hrs → Travel Batta
    - >50 km & >6 hrs → Food Allowance
    - Otherwise → No Allowance
    """
    distance = float(distance_travelled_km or 0)
    hours = float(total_hours or 0)
    is_overnight_stay = int(is_overnight_stay or 0)
    is_outside_kerala = int(is_travelling_outside_kerala or 0)

    # Get the batta policy for this designation
    policies = frappe.get_all("Batta Policy", filters={"designation": designation}, fields=["*"])
    if not policies:
        frappe.throw(f"No Batta Policy found for designation {designation}")
    policy = policies[0]

    response = {
        "daily_batta_with_overnight_stay": 0,
        "daily_batta_without_overnight_stay": 0,
        "food_allowance": {"break_fast": 0, "lunch": 0, "dinner": 0}
    }

    # --- 1️⃣ Overnight stay → Travel Batta ---
    if is_overnight_stay:
        if is_outside_kerala:
            response["daily_batta_with_overnight_stay"] = policy.get("outside_kerala__", 0)
        else:
            response["daily_batta_with_overnight_stay"] = policy.get("inside_kerala__", 0)
        return response

    # --- 2️⃣ >100 km & >=8 hours → Travel Batta ---
    if distance > 100 and hours >= 8:
        if is_outside_kerala:
            response["daily_batta_without_overnight_stay"] = policy.get("outside_kerala", 0)
        else:
            response["daily_batta_without_overnight_stay"] = policy.get("inside_kerala", 0)
        return response

    # --- 3️⃣ >50 km & >6 hours → Food Allowance ---
    if distance > 50 and hours > 6:
        response["food_allowance"] = {
            "break_fast": policy.get("break_fast", 0),
            "lunch": policy.get("lunch", 0),
            "dinner": policy.get("dinner", 0)
        }
        return response

    # --- 4️⃣ Not eligible ---
    return response
