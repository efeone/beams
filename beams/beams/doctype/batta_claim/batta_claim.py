# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BattaClaim(Document):
    def on_submit(self):
        if self.workflow_state == 'Approved':
            if self.batta_type == 'External':
                self.create_purchase_invoice_from_batta_claim()
            elif self.batta_type == 'Internal':
                self.create_journal_entry_from_batta_claim()

    def create_purchase_invoice_from_batta_claim(self):
        """
        	Creation of Purchase Invoice On The Approval Of the Batta Claim.
        """
        purchase_invoice = frappe.new_doc('Purchase Invoice')
        purchase_invoice.supplier = self.supplier
        purchase_invoice.posting_date = frappe.utils.nowdate()
        purchase_invoice.due_date = frappe.utils.add_days(purchase_invoice.posting_date, 30)

        purchase_invoice.append('items', {
            'item_code': 'Batta Claim',
            'rate': self.total_driver_batta,
            'qty': 1
        })

        purchase_invoice.insert()
        purchase_invoice.submit()

    def create_journal_entry_from_batta_claim(self):
        """
        	Creation of Journal Entry On The Approval Of the Batta Claim.
        """
        journal_entry = frappe.new_doc('Journal Entry')
        journal_entry.posting_date = frappe.utils.nowdate()
        journal_entry.party_type = 'Employee'

        journal_entry.append('accounts', {
            'account': 'Payroll Payable - E',
            'party_type': 'Employee',
            'party': self.employee,
            'debit_in_account_currency': self.total_driver_batta,
            'credit_in_account_currency': 0,
        })

        journal_entry.append('accounts', {
            'account': 'Payroll Payable - E',
            'party_type': 'Employee',
            'party': self.employee,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': self.total_driver_batta,
        })

        journal_entry.insert()
        journal_entry.submit()
