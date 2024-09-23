# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

class SubstituteBooking(Document):
    def on_submit(self):
        """
        This method is triggered when the workflow state is 'Approved'.
        It generates a Journal Entry by calling 'create_journal_entry_from_substitute_booking'.
        """
        if self.workflow_state == 'Approved':
            self.create_journal_entry_from_substitute_booking()

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
        # Create a new Journal Entry
        journal_entry = frappe.new_doc('Journal Entry')
        journal_entry.posting_date = frappe.utils.nowdate()
        # Append credit entry
        journal_entry.append('accounts', {
            'account': default_credit_account,
            'party_type': 'Employee',
            'party': self.substituting_for,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': self.total_wage,
        })
        # Append debit entry
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
