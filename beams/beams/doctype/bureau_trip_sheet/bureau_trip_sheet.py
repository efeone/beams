#  Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_datetime, getdate


class BureauTripSheet(Document):
    def validate(self):
        self.calculate_batta()
        self.calculate_total_distance_travelled()
        self.calculate_hours()
        self.calculate_total_daily_batta()
        self.calculate_total_ot_batta()

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

        # Set the 'total_distance_travelled_km' field with the calculated sum
        self.total_distance_travelled_km = total_distance

    def calculate_hours(self):
        '''
        Calculate the total hours worked by summing up the 'total_hours' values from work details.
        '''
        total_hours = 0

        if self.work_details:
            for row in self.work_details:
                if row.total_hours:
                    total_hours += float(row.total_hours)

        # Set the 'total_distance_travelled_km' field with the calculated sum
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

        # Set the 'total_distance_travelled_km' field with the calculated sum
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

        # Set the 'total_distance_travelled_km' field with the calculated sum
        self.total_ot_batta = total_ot_batta

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
                # Check for both start and end dates
                for date_threshold in [getdate(from_date_time), getdate(to_date_time)]:
                    if check_meal_time(from_date_time, to_date_time, date_threshold, start_time, end_time):
                        values[meal] += allowance

    return values

def check_meal_time(from_date_time, to_date_time, date_threshold, start_time, end_time):
    start_datetime = get_datetime('{} {}'.format(date_threshold, start_time))
    end_datetime = get_datetime('{} {}'.format(date_threshold, end_time))
    return (from_date_time <= start_datetime <= to_date_time) or (from_date_time <= end_datetime <= to_date_time)

@frappe.whitelist()
def calculate_batta_allowance(designation=None, is_travelling_outside_kerala=0, is_overnight_stay=0, total_distance_travelled_km=0, total_hours=0):
    '''
        Calculation Of Total Batta Allowance based on Batta Policy
    '''
    #Convert inputs to proper types
    def sanitize_number(value):
        try:
            return float(value)
        except:
            return 0
    total_distance_travelled_km = sanitize_number(total_distance_travelled_km)
    total_hours = sanitize_number(total_hours)

    # Fetch the Batta Policy for the given designation
    batta_policy = frappe.get_all('Batta Policy', filters={'designation': 'Driver'}, fields=['*'])
    if not batta_policy:
        frappe.throw(f"No Batta Policy found for the designation: {designation}")
        return {"batta": 0}

    policy = batta_policy[0]

    # Get policy checkbox values
    is_actual_daily_batta = policy.get('is_actual_') or 0  # Daily Batta with Overnight Stay Checkbox
    is_actual_daily_batta_without_overnight = policy.get('is_actual__') or 0  # Daily Batta Without Overnight Stay Checkbox

    # Convert inputs to boolean
    is_travelling_outside_kerala = bool(int(is_travelling_outside_kerala or 0))
    is_overnight_stay = bool(int(is_overnight_stay or 0))

    # Initialize batta values
    daily_batta_with_overnight_stay = 0
    daily_batta_without_overnight_stay = 0

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
            if total_distance_travelled_km > 100 and total_hours >= 8: # Additional condition
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
