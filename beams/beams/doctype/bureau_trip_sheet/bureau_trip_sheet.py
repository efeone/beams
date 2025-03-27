#  Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

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
