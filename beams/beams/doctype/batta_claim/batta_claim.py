# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
import re
from frappe.utils import getdate, get_datetime, date_diff, add_days, flt, cint
import math
from frappe.model.document import Document


class BattaClaim(Document):
	def before_insert(self):
		self.set_from_bureau_flag()

	def set_from_bureau_flag(self):
		"""
		Sets the 'from_bureau' flag to 1 if the creating user has the
		'Bureau User' role.
		"""
		user = frappe.session.user
		if "Bureau User" in frappe.get_roles(user):
			self.from_bureau = 1

	def on_submit(self):
		if self.workflow_state in ["Approved by CEO", "Approved"] and self.docstatus == 1:
			if not self.expense_type:
				frappe.throw(
					title="Expense Type Required",
					msg=_("Please select Expense Type")
				)
			if self.batta_type == 'External':
				self.create_purchase_invoice_from_batta_claim()
			elif self.batta_type == 'Internal':
				self.create_journal_entry_from_batta_claim()

	def validate(self):
		self.assign_hod_role()
		self.calculate_total_hours()
		self.calculate_total_distance_travelled()
		self.calculate_daily_batta()
		self.calculate_total_daily_batta()
		self.calculate_batta()
		self.calculate_total_batta()

	def create_purchase_invoice_from_batta_claim(self):
		'''
			Creation of Purchase Invoice on The Approval Of the Batta Claim.
		'''
		purchase_invoice = frappe.new_doc('Purchase Invoice')
		purchase_invoice.supplier = self.supplier
		purchase_invoice.batta_claim_reference = self.name
		purchase_invoice.posting_date = frappe.utils.nowdate()
		purchase_invoice.due_date = frappe.utils.add_days(purchase_invoice.posting_date, 30)
		batta_claim_service_item = frappe.db.get_single_value('Beams Accounts Settings', 'batta_claim_service_item')
		purchase_invoice.append('items', {
			'item_code': batta_claim_service_item,
			'rate': self.total_driver_batta,
			'qty': 1
		})

		purchase_invoice.insert()
		purchase_invoice.submit()

	def create_journal_entry_from_batta_claim(self):
		'''
			Creation of Journal Entry on the Approval of the Batta Claim.
		'''
		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.batta_claim_reference = self.name
		journal_entry.posting_date = frappe.utils.nowdate()
		batta_payable_account = frappe.db.get_single_value('Beams Accounts Settings', 'batta_payable_account')
		direct_expense_account = frappe.db.get_single_value('Beams Accounts Settings', 'batta_expense_account')
		indirect_expense_account = frappe.db.get_single_value('Beams Accounts Settings', 'default_indirect_expense_account')

		# Validate that both accounts are set
		if not batta_payable_account:
			frappe.throw(
				title="Batta Payable Account Not Configured",
				msg=_("Please configure the Batta Payable Account in the Beams Accounts Settings.")
			)
		if not direct_expense_account:
			frappe.throw(
				title="Direct Expense Account Missing",
				msg=_("Default Direct Expense Account is not set. Please configure it in Beams Accounts Settings.")
			)
		if not indirect_expense_account:
			frappe.throw(
				title="Indirect Expense Account Missing",
				msg=_("Default Indirect Expense Account is not set in Beams Accounts Settings.")
			)

		if self.expense_type == 'Direct':
				selected_expense_account = direct_expense_account
		else:
				selected_expense_account = indirect_expense_account

		journal_entry.append('accounts', {
			'account': batta_payable_account,
			'party_type': 'Employee',
			'party': self.employee,
			'debit_in_account_currency': self.total_daily_batta,
			'credit_in_account_currency': 0,
		})
		journal_entry.append('accounts', {
			'account': selected_expense_account,
			'debit_in_account_currency': 0,
			'credit_in_account_currency': self.total_daily_batta,
		})
		journal_entry.insert()
		frappe.msgprint(f"Journal Entry {journal_entry.name} has been created successfully.", alert=True,indicator="green")

	def calculate_total_distance_travelled(self):
		'''
			Calculation of Total Distance Travelled(km)
		'''
		total_distance = 0

		if self.work_detail:
			for row in self.work_detail:
				if row.distance_travelled_km:
					total_distance += row.distance_travelled_km

		# Set the 'total_distance_travelled_km' field with the calculated sum
		self.total_distance_travelled_km = total_distance

	def calculate_total_hours(self):
		'''
			Calculation Of Total Hours
		'''
		total_hours = 0

		if self.work_detail:
			for row in self.work_detail:
				if row.total_hours:
					total_hours += float(row.total_hours)

		self.total_hours = total_hours

	def calculate_total_daily_batta(self):
		'''
		Calculation of Total Daily Batta
		- If policy is ACTUAL → take manual parent values directly
		- Else → calculate from rows
		'''
		rows_total = 0.0
		sum_food = 0.0

		for row in self.get("work_detail") or []:
			rows_total += flt(row.daily_batta or 0)
			sum_food += flt(row.total_food_allowance or 0)

		is_actual_with = 0
		is_actual_without = 0

		if self.designation:
			batta_policy = frappe.get_all(
				'Batta Policy',
				filters={'designation': self.designation},
				fields=['is_actual_', 'is_actual__'],
				limit=1
			)
			if batta_policy:
				is_actual_with = cint(batta_policy[0].get('is_actual_', 0))
				is_actual_without = cint(batta_policy[0].get('is_actual__', 0))

		parent_components = 0.0

		if is_actual_with:
			parent_components += flt(self.daily_batta_with_overnight_stay or 0)

		if is_actual_without:
			parent_components += flt(self.daily_batta_without_overnight_stay or 0)

		parent_components += flt(self.room_rent_batta or 0)

		self.total_daily_batta = flt(rows_total + sum_food + parent_components)

	def calculate_batta(self):
		'''
			Calculation of Total Batta based on room rent batta,daily batta with overnight stay and daily batta without Overnight stay
		'''
		self.batta = (self.room_rent_batta or 0) \
					+ (self.daily_batta_without_overnight_stay or 0) \
					+ (self.daily_batta_with_overnight_stay or 0)
		
	def calculate_daily_batta(self):
		"""
		Auto creation logic:

			✔ 100+ KM AND >= 8 Hours      → BATTA (no food allowance)
			✔ 50-100 KM AND >= 6 Hours    → Food Allowance
			✔ 100+ KM AND 6-8 Hours       → Food Allowance
			✔ Else → No Allowance

		When policy is Actual (relevant flag=1):
		- Skip all resets and calculations for that component.
		- Preserve manual entries in fields (e.g., row.daily_batta, row.breakfast).
		- Parent fields (e.g., daily_batta_without_overnight_stay) are not reset/overridden.
		"""
		if not self.get("work_detail"):
			return

		batta_policy = frappe.get_all('Batta Policy', filters={'designation': self.designation}, fields=['*'])
		if not batta_policy:
			return
		policy = batta_policy[0]

		is_actual_with = cint(policy.get('is_actual_', 0))
		is_actual_without = cint(policy.get('is_actual__', 0))
		is_actual_food = cint(policy.get('is_actual___', 0))

		if not is_actual_without:
			self.daily_batta_without_overnight_stay = 0
		if not is_actual_with:
			self.daily_batta_with_overnight_stay = 0

		for row in self.work_detail:
			total_hours = flt(row.total_hours or 0)
			distance = flt(row.distance_travelled_km or 0)
			row.number_of_days = max(1, math.ceil(total_hours / 24))

			full_batta_condition = (distance >= 100 and total_hours >= 8)
			food_condition = (not self.is_overnight_stay and
							((50 <= distance < 100 and total_hours >= 6) or
							(distance >= 100 and 6 <= total_hours < 8)))

			if full_batta_condition:
				if self.is_overnight_stay:
					actual_flag = is_actual_with
					rate_key = "daily_batta_with_overnight_stay"
					parent_field = "daily_batta_with_overnight_stay"
				else:
					actual_flag = is_actual_without
					rate_key = "daily_batta_without_overnight_stay"
					parent_field = "daily_batta_without_overnight_stay"

				if not actual_flag:
					batta_data = calculate_batta_allowance(
						designation=self.designation,
						is_travelling_outside_kerala=self.is_travelling_outside_kerala,
						is_overnight_stay=self.is_overnight_stay,
						is_avail_room_rent=self.is_avail_room_rent,
						total_distance_travelled_km=distance,
						total_hours=total_hours
					)
					parent_rate = flt(batta_data.get(rate_key, 0))
					setattr(self, parent_field, parent_rate)
					row.daily_batta = row.number_of_days * parent_rate
				continue

			actual_flag = is_actual_without

			if food_condition:
				if not is_actual_food:
					values = get_batta_for_food_allowance(
						designation=self.designation,
						from_date_time=row.from_date_and_time,
						to_date_time=row.to_date_and_time,
						total_hrs=total_hours
					)
					row.breakfast = values.get("break_fast", 0)
					row.lunch = values.get("lunch", 0)
					row.dinner = values.get("dinner", 0)
					row.total_food_allowance = (
						flt(row.breakfast) + flt(row.lunch) + flt(row.dinner)
					)
				if not actual_flag:
					row.daily_batta = 0
				continue

			if not actual_flag and not self.is_overnight_stay:
				row.daily_batta = 0
			if not is_actual_food:
				row.breakfast = 0
				row.lunch = 0
				row.dinner = 0
				row.total_food_allowance = 0

	def calculate_total_batta(self):
		"""
		Server-side equivalent of JS calculate_total_batta.
		Calculates total_batta = daily_batta + total_food_allowance for each row.
		"""
		if not self.get('work_detail'):
			return

		for row in self.work_detail:
			daily_batta = row.daily_batta or 0
			food_allowance = row.total_food_allowance or 0
			row.total_batta = daily_batta + food_allowance

	def assign_hod_role(self):
		'''
			Set the Head of Department (HOD) for the Leave Application based on the Employee's department.
		'''
		if not self.employee or self.hod_email:
			return

		department = frappe.db.get_value(
			"Employee",
			self.employee,
			"department"
		)
		if not department:
			return

		hod_employee = frappe.db.get_value(
			"Department",
			department,
			"head_of_department"
		)
		if not hod_employee:
			return

		hod_user = frappe.db.get_value(
			"Employee",
			hod_employee,
			"user_id"
		)
		if not hod_user:
			return

		self.hod_email = hod_user


@frappe.whitelist()
def calculate_batta_allowance(designation=None, is_travelling_outside_kerala=0, is_overnight_stay=0, is_avail_room_rent=0, total_distance_travelled_km=0, total_hours=0):
	'''
		Calculation Of Total Batta Allowance based on Batta Policy
	'''
	# Convert inputs to proper types
	def sanitize_number(value):
		"""Extract a valid float from a string by keeping only the first valid decimal number."""
		if isinstance(value, str):
			match = re.search(r'\d+(\.\d+)?', value)
			return float(match.group()) if match else 0.0
		return float(value or 0.0)

	# Convert inputs safely
	total_distance_travelled_km = sanitize_number(total_distance_travelled_km)
	total_hours = sanitize_number(total_hours)

	# Fetch the Batta Policy for the given designation
	batta_policy = frappe.get_all('Batta Policy', filters={'designation': designation}, fields=['*'])
	if not batta_policy:
		frappe.throw(f"No Batta Policy found for the designation: {designation}")
		return {"batta": 0}

	policy = batta_policy[0]

	# Get policy checkbox values
	is_actual_room_rent = policy.get('is_actual') or 0  # Room Rent Checkbox
	is_actual_daily_batta = policy.get('is_actual_') or 0  # Daily Batta with Overnight Stay Checkbox
	is_actual_daily_batta_without_overnight = policy.get('is_actual__') or 0  # Daily Batta Without Overnight Stay Checkbox

	# Convert inputs to boolean
	is_travelling_outside_kerala = bool(int(is_travelling_outside_kerala or 0))
	is_overnight_stay = bool(int(is_overnight_stay or 0))
	is_avail_room_rent = bool(int(is_avail_room_rent or 0))

	# Initialize batta values
	room_rent_batta = 0
	daily_batta_with_overnight_stay = 0
	daily_batta_without_overnight_stay = 0

	# Calculate Room Rent Batta
	if is_overnight_stay and is_avail_room_rent:
		if not is_actual_room_rent:  # Check if policy is not actual
			if is_travelling_outside_kerala:
				room_rent_batta = float(policy.get('outside_kerala_', 0))
			else:
				room_rent_batta = float(policy.get('inside_kerala_', 0))

	# Calculate Daily Batta with Overnight Stay
	if not is_actual_daily_batta:  # Check if policy is not actual
		if is_overnight_stay:
			if is_travelling_outside_kerala:
				daily_batta_with_overnight_stay = float(policy.get('outside_kerala__', 0))
			else:
				daily_batta_with_overnight_stay = float(policy.get('inside_kerala__', 0))

	# Calculate Daily Batta without Overnight Stay
	if not is_actual_daily_batta_without_overnight:  # Check if policy is not actual
		if not is_overnight_stay:  # Ensure overnight stay is NOT checked
			if total_distance_travelled_km >= 100 and total_hours >= 8: # Additional condition
				if is_travelling_outside_kerala:
					daily_batta_without_overnight_stay = float(policy.get('outside_kerala', 0))
				else:
					daily_batta_without_overnight_stay = float(policy.get('inside_kerala', 0))

	return {
		"room_rent_batta": room_rent_batta,
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
def get_batta_for_food_allowance(designation, from_date_time, to_date_time, total_hrs, is_delhi_bureau=False):
	'''
		Method to get Batta for Food
	'''
	values = { 'break_fast': 0, 'lunch': 0, 'dinner': 0 }
	batta_policy = frappe.db.exists('Batta Policy', { 'designation': designation })
	from_date_time = get_datetime(from_date_time)
	to_date_time = get_datetime(to_date_time)
	required_hours = 4 if is_delhi_bureau else 6

	if batta_policy and float(total_hrs) > required_hours:
		is_actual = frappe.db.get_value('Batta Policy', batta_policy, 'is_actual___')
		if is_actual:
			return values

		break_fast, lunch, dinner = frappe.db.get_value('Batta Policy', batta_policy, ['break_fast', 'lunch', 'dinner'])

		current_date = getdate(from_date_time)
		end_date = getdate(to_date_time)

		while current_date <= end_date:
			# Define meal timings for the current day
			break_fast_start_time = get_datetime(f'{current_date} 04:00')
			break_fast_end_time = get_datetime(f'{current_date} 09:00')
			lunch_start_time = get_datetime(f'{current_date} 12:30')
			lunch_end_time = get_datetime(f'{current_date} 14:00')
			dinner_start_time = get_datetime(f'{current_date} 18:00')
			dinner_end_time = get_datetime(f'{current_date} 21:00')

			# Check Breakfast
			if (from_date_time <= break_fast_start_time <= to_date_time) or (from_date_time <= break_fast_end_time <= to_date_time):
				values['break_fast'] += break_fast

			# Check Lunch
			if (from_date_time <= lunch_start_time <= to_date_time) or (from_date_time <= lunch_end_time <= to_date_time):
				values['lunch'] += lunch

			# Check Dinner
			if (from_date_time <= dinner_start_time <= to_date_time) or (from_date_time <= dinner_end_time <= to_date_time):
				values['dinner'] += dinner

			# Move to the next day
			current_date = add_days(current_date, 1)

	return values

@frappe.whitelist()
def calculate_total_food_allowance(breakfast=0, lunch=0, dinner=0):
	try:
		total = (frappe.utils.flt(breakfast) +
				 frappe.utils.flt(lunch) +
				 frappe.utils.flt(dinner))
		return {"total_food_allowance": total}
	except Exception as e:
		return {
			"total_food_allowance": 0
		}

@frappe.whitelist()
def calculate_total_batta(daily_batta=0, total_food_allowance=0):
	try:
		total = (frappe.utils.flt(daily_batta) +
				 frappe.utils.flt(total_food_allowance))
		return {"total_batta": total}
	except Exception as e:
		return {
			"total_batta": 0
		}