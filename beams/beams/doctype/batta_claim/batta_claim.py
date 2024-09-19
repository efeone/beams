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

        # Loop through the work_detail child table
        for row in doc.get('work_detail', []):
            total_daily_batta += row.get('daily_batta', 0)
            total_ot_batta += row.get('ot_batta', 0)

        # Total batta is the sum of total_daily_batta and total_ot_batta
        total_driver_batta = total_daily_batta + total_ot_batta
        return {
            'total_daily_batta': total_daily_batta,
            'total_ot_batta': total_ot_batta,
            'total_driver_batta': total_driver_batta
        }
