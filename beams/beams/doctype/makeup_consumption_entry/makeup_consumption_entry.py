# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class MakeupConsumptionEntry(Document):

    def on_submit(self):
        self.create_stock_entry()

    def on_cancel(self):
        self.cancel_stock_entry()

    def create_stock_entry(self):
        '''
        Creates a Stock Entry (Material Issue) for the items listed
        in the Makeup Consumption Entry document and links it.
        '''
        # Create a new Stock Entry
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Issue"

        # Add items from Makeup Consumption Entry to Stock Entry
        for item in self.items:
            stock_entry.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "s_warehouse": self.source_warehouse,
            })

        # Save and Submit the Stock Entry
        stock_entry.insert()
        stock_entry.submit()

        # Link the Stock Entry to the current Makeup Consumption Entry
        self.db_set("stock_entry", stock_entry.name)

        # Notify user
        frappe.msgprint(_("Stock entry {0} created successfully.").format(stock_entry.name), alert=True)

    def cancel_stock_entry(self):
        '''
        Cancels the linked Stock Entry when the Makeup Consumption Entry is canceled.
        '''
        if self.stock_entry:
            # Fetch the linked Stock Entry
            stock_entry = frappe.get_doc("Stock Entry", self.stock_entry)

            # Cancel the Stock Entry if its status is Submitted
            if stock_entry.docstatus == 1:  # 1 means Submitted
                stock_entry.cancel()
                frappe.msgprint(_("Linked Stock Entry {0} has been canceled.").format(self.stock_entry), alert=True)
