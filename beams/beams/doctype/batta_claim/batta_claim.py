# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import getdate, get_datetime, date_diff
from frappe.model.document import Document


class BattaClaim(Document):
    def on_submit(self):
        if self.workflow_state == 'Approved':
            if self.batta_type == 'External':
                self.create_purchase_invoice_from_batta_claim()
            elif self.batta_type == 'Internal':
                self.create_journal_entry_from_batta_claim()

    def validate(self):
        self.calculate_total_distance_travelled()
        self.calculate_total_daily_batta()
        self.calculate_batta()
        self.calculate_total_hours()

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
        batta_expense_account = frappe.db.get_single_value('Beams Accounts Settings', 'batta_expense_account')
        # Validate that both accounts are set
        if not batta_payable_account and not batta_expense_account:
            frappe.throw("Please configure both the Batta Payable Account and the Batta Expense Account in the Beams Accounts Settings.")
        # Validate that both accounts are set
        if not batta_payable_account:
            frappe.throw("Please configure the Batta Payable Account in the Beams Accounts Settings.")
        if not batta_expense_account:
            frappe.throw("Please configure the Batta Expense  Account in the Beams Accounts Settings..")

        journal_entry.append('accounts', {
            'account': batta_payable_account,
            'party_type': 'Employee',
            'party': self.employee,
            'debit_in_account_currency': self.total_driver_batta,
            'credit_in_account_currency': 0,
        })
        journal_entry.append('accounts', {
            'account': batta_expense_account,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': self.total_driver_batta,
        })
        journal_entry.insert()
        journal_entry.submit()
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
        '''
        total_daily_batta = 0

        if self.work_detail:
            for row in self.work_detail:
                if row.total_batta:
                    total_daily_batta += row.total_batta

        # Set the 'total_distance_travelled_km' field with the calculated sum
        self.total_daily_batta = total_daily_batta

    def calculate_batta(self):
        '''
            Calculation of Total Batta based on room rent batta,daily batta with overnight stay and daily batta without Overnight stay
        '''
        self.batta = (self.room_rent_batta or 0) \
                   + (self.daily_batta_without_overnight_stay or 0) \
                   + (self.daily_batta_with_overnight_stay or 0)

@frappe.whitelist()
def calculate_batta_allowance(designation=None, is_travelling_outside_kerala=0, is_overnight_stay=0, is_avail_room_rent=0, total_distance_travelled_km=0, total_hours=0):
    '''
        Calculation Of Total Batta Allowance based on Batta Policy
    '''
    # Convert inputs to proper types
    total_distance_travelled_km = float(total_distance_travelled_km or 0)
    total_hours = float(total_hours or 0)

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
                daily_batta_with_overnight_stay = float(policy.get('outside_kerala_', 0))
            else:
                daily_batta_with_overnight_stay = float(policy.get('inside_kerala_', 0))

    # Calculate Daily Batta without Overnight Stay
    if not is_actual_daily_batta_without_overnight:  # Check if policy is not actual
        if not is_overnight_stay:  # Ensure overnight stay is NOT checked
            if total_distance_travelled_km > 100 and total_hours >= 8: # Additional condition
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
    values = { 'break_fast':0, 'lunch':0, 'dinner':0 }
    batta_policy = frappe.db.exists('Batta Policy', { 'designation':designation })
    from_date_time = get_datetime(from_date_time)
    to_date_time = get_datetime(to_date_time)
    required_hours = 4 if is_delhi_bureau else 6
    if batta_policy and float(total_hrs)>required_hours:
        is_actual = frappe.db.get_value('Batta Policy', batta_policy, 'is_actual___')
        if is_actual:
            return values
        break_fast, lunch, dinner = frappe.db.get_value('Batta Policy', batta_policy, ['break_fast', 'lunch', 'dinner'])
        same_date = False
        if getdate(from_date_time) == getdate(to_date_time):
            same_date = True
        #Breakfast check
        if same_date:
            date_threshold = getdate(from_date_time)
            break_fast_start_time = get_datetime('{0} {1}'.format(date_threshold, '04:00'))
            break_fast_end_time = get_datetime('{0} {1}'.format(date_threshold, '09:00'))
            if (from_date_time <= break_fast_start_time <= to_date_time) or (from_date_time <= break_fast_end_time <= to_date_time):
                values['break_fast'] = break_fast
            lunch_start_time = get_datetime('{0} {1}'.format(date_threshold, '12:30'))
            lunch_end_time = get_datetime('{0} {1}'.format(date_threshold, '14:00'))
            if (from_date_time <= lunch_start_time <= to_date_time) or (from_date_time <= lunch_end_time <= to_date_time):
                values['lunch'] = lunch
            dinner_start_time = get_datetime('{0} {1}'.format(date_threshold, '18:00'))
            dinner_end_time = get_datetime('{0} {1}'.format(date_threshold, '21:00'))
            if (from_date_time <= dinner_start_time <= to_date_time) or (from_date_time <= dinner_end_time <= to_date_time):
                values['dinner'] = dinner
        else:
            #Breakfast check
            date_threshold = getdate(from_date_time) #Check with Start Date
            break_fast_start_time = get_datetime('{0} {1}'.format(date_threshold, '04:00'))
            break_fast_end_time = get_datetime('{0} {1}'.format(date_threshold, '09:00'))
            if (from_date_time <= break_fast_start_time <= to_date_time) or (from_date_time <= break_fast_end_time <= to_date_time):
                values['break_fast'] = break_fast
            date_threshold = getdate(to_date_time) #Check with End Date
            break_fast_start_time = get_datetime('{0} {1}'.format(date_threshold, '04:00'))
            break_fast_end_time = get_datetime('{0} {1}'.format(date_threshold, '09:00'))
            if (from_date_time <= break_fast_start_time <= to_date_time) or (from_date_time <= break_fast_end_time <= to_date_time):
                values['break_fast'] = values.get('break_fast', 0) + break_fast
            #Lunch Check
            date_threshold = getdate(from_date_time) #Check with Start Date
            lunch_start_time = get_datetime('{0} {1}'.format(date_threshold, '12:30'))
            lunch_end_time = get_datetime('{0} {1}'.format(date_threshold, '14:00'))
            if (from_date_time <= lunch_start_time <= to_date_time) or (from_date_time <= lunch_end_time <= to_date_time):
                values['lunch'] = lunch
            date_threshold = getdate(to_date_time) #Check with End Date
            lunch_start_time = get_datetime('{0} {1}'.format(date_threshold, '12:30'))
            lunch_end_time = get_datetime('{0} {1}'.format(date_threshold, '14:00'))
            if (from_date_time <= lunch_start_time <= to_date_time) or (from_date_time <= lunch_end_time <= to_date_time):
                values['lunch'] = values.get('lunch', 0) + lunch
            #Dinner Check
            date_threshold = getdate(from_date_time) #Check with Start Date
            dinner_start_time = get_datetime('{0} {1}'.format(date_threshold, '18:00'))
            dinner_end_time = get_datetime('{0} {1}'.format(date_threshold, '21:00'))
            if (from_date_time <= dinner_start_time <= to_date_time) or (from_date_time <= dinner_end_time <= to_date_time):
                values['dinner'] = dinner
            date_threshold = getdate(to_date_time) #Check with End Date
            dinner_start_time = get_datetime('{0} {1}'.format(date_threshold, '18:00'))
            dinner_end_time = get_datetime('{0} {1}'.format(date_threshold, '21:00'))
            if (from_date_time <= dinner_start_time <= to_date_time) or (from_date_time <= dinner_end_time <= to_date_time):
                values['dinner'] = values.get('dinner', 0) + dinner
    return values
