# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from frappe import _


class MakeupConsumptionEntry(Document):

    def on_submit(self):
        self.create_stock_entry()

    def create_stock_entry(self):
        '''
        Creates a Stock Entry (Material Issue) for the items listed
        in the Makeup Consumption Entry document.
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
                "allow_zero_valuation_rate": 1,
            })

        # Save and Submit the Stock Entry
        stock_entry.insert()
        stock_entry.submit()

        # Notify user
        frappe.msgprint(
            _(f'Stock Entry {get_link_to_form("Stock Entry", stock_entry.name)} created successfully!')
        )
