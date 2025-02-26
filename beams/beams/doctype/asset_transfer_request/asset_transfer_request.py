# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _
from frappe.utils import now_datetime, get_url_to_form
from datetime import datetime


class AssetTransferRequest(Document):
    def before_save(self):
        self.validate_posting_date()

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))

    def on_update_after_submit(self):
        '''Ensure that Asset Movement and Stock Entries are created when the workflow state is 'Transferred'.'''
        if self.workflow_state == 'Transferred':
            self.create_asset_movement()
            self.create_stock_entries()

    def create_asset_movement(self):
        """Create Asset Movement when the workflow state is 'Transferred'."""
        asset_movement = frappe.new_doc('Asset Movement')
        asset_movement.purpose = 'Transfer'
        asset_movement.posting_time = self.posting_time
        asset_movement.reference_doctype = "Asset Transfer Request"
        asset_movement.reference_name = self.name
        posting_datetime_str = f"{self.posting_date} {self.posting_time}"
        asset_movement.transaction_date = datetime.strptime(posting_datetime_str, "%Y-%m-%d %H:%M:%S")

        if not self.location:
            frappe.throw(_("Please provide a target location for the asset transfer."))

        if not self.assets and self.asset_type == "Bundle":
            frappe.throw(_("No assets found to transfer."))
        elif not self.asset and self.asset_type == "Single Asset":
            frappe.throw(_("Asset required for transfer."))

        if self.asset_type == "Single Asset":
            if self.asset:
                asset_movement.append('assets', {
                    "asset": self.asset,
                    "target_location": self.location,
                })
        elif self.asset_type == "Bundle":

            for item in self.assets:
                if item.asset:
                    asset_movement.append('assets', {
                        "asset": item.asset,
                        "target_location": self.location,
                    })

        asset_movement.insert()
        asset_movement.submit()

        frappe.msgprint(
            _('Asset Movement Created: <a href="{0}">{1}</a>').format(get_url_to_form(asset_movement.doctype, asset_movement.name),asset_movement.name),
            alert=True, indicator='green'
        )

    def create_stock_entries(self):
        """Create Stock Entry when the workflow state is 'Transferred'."""
        if not self.asset_type == "Bundle":
            return

        if not self.items:
            return

        source_warehouse = 'Stores - E'
        if not frappe.db.exists('Warehouse', source_warehouse):
            frappe.throw(_("Could not find Source Warehouse: {0}".format(source_warehouse)))

        stock_entry = frappe.new_doc('Stock Entry')
        stock_entry.stock_entry_type = 'Material Issue'
        stock_entry.purpose = 'Material Issue'
        stock_entry.from_warehouse = source_warehouse
        stock_entry.posting_time = self.posting_time
        stock_entry.set("set_posting_time", 1)
        stock_entry.posting_date = self.posting_date
        stock_entry.set("set_posting_time", 1)

        for item in self.items:
            if item.item:
                stock_entry.append('items', {
                    "item_code": item.item,
                    "qty": item.qty,
                    "s_warehouse": source_warehouse,
                })

        if not stock_entry.items:
            frappe.throw(_("No items found to add to Stock Entry."))

        stock_entry.insert()
        stock_entry.submit()

        frappe.msgprint(
            _('Stock Entry Created: <a href="{0}">{1}</a>').format(get_url_to_form(stock_entry.doctype, stock_entry.name),stock_entry.name),
            alert=True, indicator='green')

@frappe.whitelist()
def get_stock_items_from_bundle(bundle):
    stock_items = frappe.get_all(
        "Asset Bundle Stock Item",
        filters={"parent": bundle},
        fields=["item", "uom", "qty"]
    )
    return stock_items


@frappe.whitelist()
def get_asset_return_checklist_template(template_name):
    if not frappe.db.exists("Asset Return Checklist Template", template_name):
        frappe.msgprint(_("Asset Return Checklist Template '{}' not found").format(template_name))

    return frappe.get_all(
        "Asset Return Check",
        filters={"parent": template_name},
        fields=["checklist_item"]
    )

@frappe.whitelist()
def get_bundle_assets(bundle):
    if not bundle:
        return {"assets": [], "bundles": []}

    bundle_doc = frappe.get_doc("Asset Bundle", bundle)
    assets_list = bundle_doc.assets if bundle_doc.assets else []
    bundles_list = bundle_doc.bundles if bundle_doc.bundles else []

    return {"assets": assets_list, "bundles": bundles_list}
