# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role
from frappe.utils import getdate, add_days, date_diff
import json
from datetime import datetime, date, timedelta


class SubstituteBooking(Document):
    def on_submit(self):
        """
        This method is triggered when the workflow state is 'Approved'.
        It generates a Journal Entry by calling 'create_journal_entry_from_substitute_booking'.
        """
        if self.workflow_state == 'Approved':
            self.create_journal_entry_from_substitute_booking()

    def before_validate(self):
        self.validate_duplicate_assignment()  # Call the method on self

    def validate(self):
        """
        This method is called during validation before the document is saved.
        It sets the 'paid_amount' field based on the 'is_paid' field.
        """
        # Check if 'is_paid' is true
        if self.is_paid:
            # Set 'paid_amount' to the value of 'total_wage'
            self.paid_amount = self.total_wage
        else:
            # If 'is_paid' is not checked, set 'paid_amount' to None
            self.paid_amount = None


    @frappe.whitelist()
    def create_journal_entry_from_substitute_booking(self):
        """
        Creation of Journal Entry on the Approval of the Substitute Booking.
        """
        # Fetch debit and credit accounts from custom settings or any relevant logic
        default_credit_account = frappe.db.get_single_value('Beams Accounts Settings', 'default_credit_account')
        default_debit_account = frappe.db.get_single_value('Beams Accounts Settings', 'default_debit_account')
        # Validate that both debit and credit accounts are configured and different
        if not default_credit_account:
            frappe.throw("Please configure the Default Credit Account in the Beams Accounts Settings.")
        if not default_debit_account:
            frappe.throw("Please configure the Default Debit Account in the Beams Accounts Settings.")

        # Check if a Journal Entry exists for this Substitute Booking, excluding canceled entries
        journal_entry_exists = frappe.db.exists("Journal Entry", {"substitute_booking_reference": self.name,"docstatus": ["!=", 2] })
        if journal_entry_exists:
            frappe.throw("Journal Entry already exists for this Substitute Booking.")
        else :
            if self.is_paid:
                journal_entry = frappe.new_doc('Journal Entry')
                journal_entry.substitute_booking_reference = self.name
                journal_entry.posting_date = frappe.utils.nowdate()
                journal_entry.append('accounts', {
                    'account': default_credit_account,
                    'party_type': 'Employee',
                    'party': self.substituting_for,
                    'debit_in_account_currency': 0,
                    'credit_in_account_currency': self.total_wage,
                })
                journal_entry.append('accounts', {
                    'account': default_debit_account,
                    'party_type': 'Employee',
                    'party': self.substituting_for,
                    'debit_in_account_currency': self.total_wage,
                    'credit_in_account_currency': 0,
                })
                # Insert and submit the Journal Entry
                journal_entry.insert(ignore_permissions=True)
                journal_entry.submit()
                frappe.msgprint(f"Journal Entry {journal_entry.name} has been created successfully.", alert=True)
            else:
                frappe.msgprint("Please make the payment to proceed.")


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

    def after_insert(self):
        self.create_todo_on_creation_for_substitute_booking()

    def create_todo_on_creation_for_substitute_booking(self):
        """
        Create a ToDo for Accounts Manager when a new Substitute Booking is created.
        """
        users = get_users_with_role("Accounts Manager")
        if users:
            description = f"New Substitute Booking Created for {self.substituted_by}.<br>Please Review and Update Details or take Necessary Actions."
            add_assign({
                "assign_to": users,
                "doctype": "Substitute Booking",
                "name": self.name,
                "description": description
            })

    def validate_duplicate_assignment(self):
        # Iterate over each row in the child table 'substitution_bill_date'
        for row in self.substitution_bill_date:
            # Check if any other Substitute Booking exists for the same 'substituting_for' and 'date'
            duplicate_exists = frappe.db.sql("""
                SELECT
                    parent
                FROM
                    `tabSubstitute Booking`
                INNER JOIN
                    `tabSubstitution Bill Date` as sbd
                ON
                    sbd.parent = `tabSubstitute Booking`.name
                WHERE
                    `tabSubstitute Booking`.substituting_for = %s
                AND
                    sbd.date = %s
                AND
                    `tabSubstitute Booking`.name != %s
            """, (self.substituting_for, row.date, self.name))

            # If a duplicate is found, raise an error
            if duplicate_exists:
                frappe.throw(_("A substitute is already assigned for {0} on {1}. No duplicate bookings are allowed.")
                             .format(self.substituting_for, row.date))

#
# @frappe.whitelist()
# def check_leave_application(employee, dates):
#     dates = json.loads(dates)  # Parse JSON string into Python list of dates
#     leave_applications = {}
#     missing_dates = []
#
#     # Loop through the provided dates and check for approved leave applications
#     for date in dates:
#         approved_leaves = frappe.get_all("Leave Application",
#             filters={
#                 "employee": employee,
#                 "status": "Approved",
#                 "from_date": ["<=", date],
#                 "to_date": [">=", date]
#             },
#             fields=["name", "from_date", "to_date"]
#         )
#
#         if approved_leaves:
#             leave_applications[date] = approved_leaves  # Store approved leaves by date
#         else:
#             missing_dates.append(date)  # No approved leave found for this date
#
#     return {
#         "leave_applications": leave_applications,
#         "missing_dates": missing_dates
#     }



def get_filtered_leave_applications(employee, dates):
    filtered_leaves = []

    for date in dates:
        # Fetch approved leave applications that cover the current date
        approved_leaves = frappe.get_all(
            "Leave Application",
            filters={
                "employee": employee,
                "status": "Approved",
                "from_date": ["<=", date],
                "to_date": [">=", date]
            },
            fields=["name", "from_date", "to_date"]
        )

        # If there are approved leaves for this date, add them to the filtered list
        if approved_leaves:
            filtered_leaves.extend(approved_leaves)

    # Return the filtered list of leave applications without duplicates
    return {leave['name']: leave for leave in filtered_leaves}.values()
