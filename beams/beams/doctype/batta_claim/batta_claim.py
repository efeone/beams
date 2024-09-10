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
        '''
            Creation of Purchase Invoice on The Approval Of the Batta Claim.
        '''
        purchase_invoice = frappe.new_doc('Purchase Invoice')
        purchase_invoice.supplier = self.supplier
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
        journal_entry.posting_date = frappe.utils.nowdate()
        batta_payable_account = frappe.db.get_single_value('Beams Accounts Settings', 'batta_payable_account')
        batta_expense_account = frappe.db.get_single_value('Beams Accounts Settings', 'batta_expense_account')

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
