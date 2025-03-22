# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

class StringerBill(Document):
    def on_submit(self):
        if self.workflow_state == 'Approved':
            self.create_purchase_invoice_from_stringer_bill()

    def create_purchase_invoice_from_stringer_bill(self):
        """
        Creation of Purchase Invoice On The Approval Of the Stringer Bill.
        """
        # Fetch the item code from the Stringer Type
        item_code = frappe.db.get_single_value('Beams Accounts Settings', 'stringer_service_item')



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
            'rate': self.stringer_amount
        })

        # Insert and submit the document
        purchase_invoice.insert()
        purchase_invoice.save()

        # Confirm success
        frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created successfully with Stringer Bill reference {self.name}.", alert=True, indicator="green")

    def after_insert(self):
            self.create_todo_on_creation_for_stringer_bill()

    def create_todo_on_creation_for_stringer_bill(self):
            """
            Create a ToDo for Accounts Manager when a new Stringer Bill is created.
            """
            users = get_users_with_role("Accounts Manager")
            if users:
                description = f"New Stringer Bill Created for {self.supplier}.<br>Please Review and Update Details or Take Necessary Actions."
                add_assign({
                    "assign_to": users,
                    "doctype": "Stringer Bill",
                    "name": self.name,
                    "description": description
                })
