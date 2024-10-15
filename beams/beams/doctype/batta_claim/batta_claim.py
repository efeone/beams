# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class BattaClaim(Document):
    def on_submit(self):
        if self.workflow_state == 'Approved':
            if self.batta_type == 'External':
                self.create_purchase_invoice_from_batta_claim()
            elif self.batta_type == 'Internal':
                self.create_journal_entry_from_batta_claim()

    def validate(self):
        # Call the method to calculate the total distance travelled
        self.calculate_total_distance_travelled()

    def calculate_total_distance_travelled(self):
        total_distance = 0

        # Loop through the rows in the 'work_detail' child table
        if self.work_detail:
            for row in self.work_detail:
                if row.distance_travelled_km:
                    total_distance += row.distance_travelled_km

        # Set the 'total_distance_travelled_km' field with the calculated sum
        self.total_distance_travelled_km = total_distance


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
            'debit_in_account_currency': 0,
            'credit_in_account_currency': self.total_driver_batta,
        })
        journal_entry.append('accounts', {
            'account': batta_expense_account,
            'party_type': 'Employee',
            'party': self.employee,
            'debit_in_account_currency': self.total_driver_batta,
            'credit_in_account_currency': 0,
        })
        journal_entry.insert()
        journal_entry.submit()
        frappe.msgprint(f"Journal Entry {journal_entry.name} has been created successfully.", alert=True,indicator="green")

    @frappe.whitelist()
    def calculate_total_batta(doc):
        '''Function to calculate the Total Daily Batta based on data in work detail child table
            and batta
        '''
        total_daily_batta = 0
        total_ot_batta = 0

        # Loop through the work_detail child table and ensure default values are integers
        for row in doc.get('work_detail', []):
            total_daily_batta += row.get('daily_batta', 0) or 0
            total_ot_batta += row.get('ot_batta', 0) or 0

        # Total batta is the sum of total_daily_batta and total_ot_batta
        total_driver_batta = total_daily_batta + total_ot_batta
        return {
            'total_daily_batta': total_daily_batta,
            'total_ot_batta': total_ot_batta,
            'total_driver_batta': total_driver_batta
        }

    @frappe.whitelist()
    def calculate_batta(doc):
        # Ensure that all fields default to 0 if they are None
        room_rent_batta = doc.get('room_rent_batta', 0) or 0
        daily_batta_with_overnight_stay = doc.get('daily_batta_with_overnight_stay', 0) or 0
        daily_batta_without_overnight_stay = doc.get('daily_batta_without_overnight_stay', 0) or 0
        food_allowance = doc.get('food_allowance', 0) or 0

        # Calculate the total batta
        batta = room_rent_batta + daily_batta_with_overnight_stay + daily_batta_without_overnight_stay + food_allowance

        return {
            'room_rent_batta': room_rent_batta,
            'daily_batta_with_overnight_stay': daily_batta_with_overnight_stay,
            'daily_batta_without_overnight_stay': daily_batta_without_overnight_stay,
            'food_allowance': food_allowance,
            'batta': batta
        }

# Batta Policy
@frappe.whitelist()
def calculate_batta_allowance(designation, is_travelling_outside_kerala, is_overnight_stay, total_distance_travelled_km, total_hours):
    # Ensure distance and total_hours are floats or 0
    total_distance_travelled_km = float(total_distance_travelled_km or 0)
    total_hours = float(total_hours or 0)

    # Fetch the Batta Policy for the given designation
    batta_policy = frappe.get_all('Batta Policy', filters={'designation': designation}, fields=['*'])
    if not batta_policy:
        frappe.throw(f"No Batta Policy found for the designation: {designation}")
        return {"batta": 0}

    policy = batta_policy[0]
    is_actual_room_rent = policy.get('is_actual')  # Checkbox for Room Rent for Overnight Stay
    is_actual_daily_batta_with_overnight_stay = policy.get('is_actual_')  # Checkbox for Daily Batta With Overnight Stay
    is_actual_daily_batta_without_overnight_stay = policy.get('is_actual__')  # Checkbox for Daily Batta Without Overnight Stay
    is_actual_food_allowance = policy.get('is_actual___')  # Get the first (and only) policy for the designation
    total_batta = 0

    # Safely handle NoneType by using a function
    def safe_add(value):
        return float(value) if value is not None else 0

    # Convert inputs to booleans
    is_travelling_outside_kerala = bool(int(is_travelling_outside_kerala or 0))
    is_overnight_stay = bool(int(is_overnight_stay or 0))

    # Initialize daily batta and room rent variables
    daily_batta_without_overnight_stay = 0
    room_rent_batta = 0
    daily_batta_with_overnight_stay = 0
    food_allowance = 0

    # Add Daily Batta (Inside Kerala) if distance >= 50 km and total_hours >= 8
    if total_distance_travelled_km >= 50 and total_hours >= 8:
        if is_actual_daily_batta_without_overnight_stay == 0:
            if not is_overnight_stay:  # Ensure the 'is_overnight_stay' checkbox is not checked
                if is_travelling_outside_kerala:
                    outside_kerala_batta = safe_add(policy.get('outside_kerala'))
                    daily_batta_without_overnight_stay += outside_kerala_batta
                else:
                    inside_kerala_batta = safe_add(policy.get('inside_kerala'))
                    daily_batta_without_overnight_stay += inside_kerala_batta

        # Add to total_batta
        total_batta += daily_batta_without_overnight_stay

    if is_overnight_stay:
        # Handle room rent addition
        if is_actual_room_rent == 0:  # Add room rent only if checkbox is unchecked (value is 0)
            if is_travelling_outside_kerala:
                room_rent = safe_add(policy.get('outside_kerala_'))
            else:
                room_rent = safe_add(policy.get('inside_kerala_'))
            room_rent_batta += room_rent  # Add room rent value to room_rent_batta

        # Handle daily batta with overnight stay addition
        if is_actual_daily_batta_with_overnight_stay == 0:  # Add daily batta only if checkbox is unchecked (value is 0)
            if is_travelling_outside_kerala:
                daily_batta_with_overnight_stay = safe_add(policy.get('outside_kerala__'))
            else:
                daily_batta_with_overnight_stay = safe_add(policy.get('inside_kerala__'))

    # Add Room Rent and Daily Batta with Overnight Stay to total_batta
    total_batta += room_rent_batta
    total_batta += daily_batta_with_overnight_stay

    # Add Food Allowance if total distance is >= 25 km and total_hours >= 6
    if total_distance_travelled_km >= 25 and total_hours >= 6:
        if is_actual_food_allowance == 0:
            food_allowance = safe_add(policy.get('break_fast')) + safe_add(policy.get('lunch')) + safe_add(policy.get('dinner'))
            total_batta += food_allowance

    # Return all relevant values in a single dictionary
    return {
        "room_rent_batta": room_rent_batta,
        "daily_batta_with_overnight_stay": daily_batta_with_overnight_stay,
        "daily_batta_without_overnight_stay": daily_batta_without_overnight_stay,
        "food_allowance": food_allowance,
        "batta": total_batta
    }

@frappe.whitelist()
def get_batta_policy_values():
    result = frappe.db.get_value('Batta Policy', {}, ['is_actual', 'is_actual_', 'is_actual__', 'is_actual___'], as_dict=True)
    return result
