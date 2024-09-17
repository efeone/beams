# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SubstituteBooking(Document):
    def before_save(self):
        self.calculate_no_of_days()
        self.calculate_total_wage()

        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.workflow_state != self.workflow_state and self.workflow_state == "Pending Approval":
            self.check_employee_leave()

    def calculate_no_of_days(self):
        '''
            Method to calculate no of days based on dates specified in the child table Substitution Bill Date.
        '''
        dates = [row.date for row in self.substitution_bill_date if row.date]

        unique_dates = list(set(dates))

        if len(unique_dates) != len(dates):
            frappe.throw(_("Dates should be unique."))

        self.no_of_days = len(unique_dates)

    def calculate_total_wage(self):
        '''
            Method to calculate total wage based on daily wage and no of days.
        '''
        if self.no_of_days and self.daily_wage:
            self.total_wage = self.no_of_days * self.daily_wage
        else:
            self.total_wage = 0

    def check_employee_leave(self):
        '''
            Method to verify whether the employee is on leave for each specified date in the child table Substitution Bill Date.
        '''
        employee = self.substituting_for

        if self.substitution_bill_date and employee:
            for date_entry in self.substitution_bill_date:
                leave_exists = frappe.db.exists('Leave Application', {
                    'employee': employee,
                    'status': 'Approved',
                    'from_date': ('<=', date_entry.date),
                    'to_date': ('>=', date_entry.date)
                })

                if not leave_exists:
                    formatted_date = date_entry.date.strftime("%d/%m/%Y")
                    frappe.throw(f"Employee {employee} is not on leave on {formatted_date}.")
