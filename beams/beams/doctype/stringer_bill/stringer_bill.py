# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StringerBill(Document):
    def on_submit(self):
        if self.workflow_state == 'Approved':
            self.create_purchase_invoice_from_stringer_bill()

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
