# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class StringerBill(Document):
    def on_submit(self):
        if self.workflow_state == 'Approved':
            self.create_purchase_invoice_from_stringer_bill()
    def before_save(self):
        old_doc = self.get_doc_before_save()

        if old_doc and old_doc.workflow_state != self.workflow_state and self.workflow_state == "Pending Approval":
            self.check_employee_leave()
    def validate(self):
        self.validate_unique_dates()
        self.update_total_wage()


    def create_purchase_invoice_from_stringer_bill(self):
        """
        Creation of Purchase Invoice On The Approval Of the Stringer Bill.
        """
        # Fetch the item code from the Stringer Type
        item_code = frappe.get_value("Stringer Type", self.stringer_type, "item")

        if not item_code:
            frappe.throw(f"No item found for Stringer Type: {self.stringer_type}")
            return



        # Create a new Purchase Invoice
        purchase_invoice = frappe.new_doc('Purchase Invoice')
        purchase_invoice.stringer_bill_reference = self.name
        purchase_invoice.supplier = self.supplier
        purchase_invoice.invoice_type = 'Stringer Bill'  # Set invoice type to "Stringer Bill"
        purchase_invoice.posting_date = frappe.utils.nowdate()

        purchase_invoice.bureau = self.bureau
        purchase_invoice.cost_center = self.cost_center

        # Populate Child Table
        purchase_invoice.append('items', {
            'item_code': item_code,
            'qty': 1,
            'rate': self.total_wage
        })

        # Insert and submit the document
        purchase_invoice.insert()
        purchase_invoice.submit()

        # Confirm success
        frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created successfully with Stringer Bill reference {self.name}.", alert=True, indicator="green")

    def check_employee_leave(self):
        '''
            Method to verifies if the employee is on  leave for each specified date.
        '''
        employee = self.substituting_for

        if self.date and employee:
            for date_entry in self.date:
                leave_exists = frappe.db.exists('Leave Application', {
                    'employee': employee,
                    'status': 'Approved',
                    'from_date': ('<=', date_entry.date),
                    'to_date': ('>=', date_entry.date)
                })

                if not leave_exists:
                    formatted_date = date_entry.date.strftime("%d/%m/%Y")
                    frappe.throw(f"Employee {employee} is not on leave on {formatted_date}.")


    def validate_unique_dates(self):
        '''
            Validate that each date in the Stringer Bill Date table is unique.
        '''
        dates = [row.date for row in self.date]

        if len(dates) != len(set(dates)):
            frappe.throw(_('Each Date should be unique.'))
        else:
            print("All dates are unique.")

        self.update_no_of_days()

    def update_no_of_days(self):
        '''
            Update the number of unique days based on the dates in the Stringer Bill Date table.
        '''
        unique_dates = set([row.date for row in self.date])

        self.no_of_days = len(unique_dates)

    def update_total_wage(self):
        '''
            Calculate and update the total wage based on daily wage and the number of days.
        '''
        if self.daily_wage and self.no_of_days:
            self.total_wage = self.daily_wage * self.no_of_days
        else:
            self.total_wage = 0
