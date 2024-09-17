# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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
