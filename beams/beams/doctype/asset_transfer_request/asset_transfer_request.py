# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate
from frappe import _
from frappe.utils import now_datetime, get_url_to_form
from datetime import datetime

class AssetTransferRequest(Document):
    def before_save(self):
        self.validate_posting_date()
        if self.workflow_state == "Draft":
            self.validate_locations()

    def validate_locations(self):
        """Validate that source and target locations are not the same."""
        if self.asset_type == "Single Asset" and self.asset:
            asset_doc = frappe.get_doc("Asset", self.asset)
            if asset_doc.location == self.location:
                frappe.throw(_("Source and target location cannot be the same"))
        elif self.asset_type == "Bundle":
            for item in self.assets:
                if item.asset:
                    asset_doc = frappe.get_doc("Asset", item.asset)
                    if asset_doc.location == self.location:
                        frappe.throw(_("Source and target location cannot be the same"))

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if getdate(self.posting_date) > getdate(today()):
                frappe.throw(_("Posting Date cannot be set after today's date."))

    def on_update_after_submit(self):
        '''Ensure that Asset Movement and Stock Entries are created when the workflow state is 'Transferred'.
           Mark or unmark 'In Transit' checkbox based on workflow state.

           Handles updates after submission by adding  assets,items,asset to the asset return checklist when the workflow state is 'Transferred'
        '''

        if self.workflow_state == "Transferred and Received":
            existing_checklist_items = {row.checklist_item for row in self.get("asset_return_checklist")}
            assets_to_add = set()

            if self.asset_type == "Bundle":
                assets_to_add.update(row.asset for row in self.get("assets") if row.asset)
            elif self.asset_type == "Single Asset" and self.asset:
                assets_to_add.add(self.asset)

            assets_to_add.update(row.item for row in self.get("items") if row.item)
            new_assets = assets_to_add - existing_checklist_items

            if new_assets:
                for asset in new_assets:
                    self.append("asset_return_checklist", {"checklist_item": asset})

                self.save(ignore_permissions=True)

        if self.workflow_state == 'Transferred':
            # Check if asset movement already exists
            existing_asset_movement = frappe.db.exists("Asset Movement", {
                "reference_name": self.name,
                "reference_doctype": "Asset Transfer Request"
            })

            # Check if stock entry already exists
            existing_stock_entry = frappe.db.exists("Stock Entry", {
                "name": self.stock_entry
            })

            # Only create if they don't exist
            if not existing_asset_movement:
                self.create_asset_movement()

            # Only create stock entry if it does not exist
            if not existing_stock_entry and not self.stock_entry:
                self.create_stock_entries()

            # Handle 'in_transit' flag for assets
            if self.asset_type == 'Single Asset' and self.asset:
                asset = frappe.get_doc('Asset', self.asset)
                asset.in_transit = 1 if self.workflow_state == 'Approved' else 0
                asset.save()
            elif self.asset_type == 'Bundle':
                for asset in self.assets:
                    asset_doc = frappe.get_doc('Asset', asset.asset)
                    asset_doc.in_transit = 1 if self.workflow_state == 'Approved' else 0
                    asset_doc.save()

        if self.asset_type == 'Single Asset' and self.asset:
            asset = frappe.get_doc('Asset', self.asset)
            asset.in_transit = 1 if self.workflow_state == 'Approved' else 0
            asset.save()
        elif self.asset_type == 'Bundle':
            for asset in self.assets:
                asset_doc = frappe.get_doc('Asset', asset.asset)
                asset_doc.in_transit = 1 if self.workflow_state == 'Approved' else 0
                asset_doc.save()
        self.validate_recieved_by()

        old_doc = self.get_doc_before_save()

        if old_doc:
            previous_state = old_doc.workflow_state
            current_state = self.workflow_state

            if previous_state != current_state and current_state == "Returned":
                # Workflow has changed to "Returned"
                all_movements = frappe.get_all("Asset Movement", filters={
                    "reference_doctype": "Asset Transfer Request",
                    "reference_name": self.name,
                    "purpose": "Transfer"
                })

                if len(all_movements) < 2:
                    self.create_asset_movement_on_return()

        if self.workflow_state == 'Returned':
            existing_return_stock_entry = frappe.db.exists("Stock Entry", {
                "stock_entry_type": "Material Receipt",
                "remarks": ["like", f"%{self.name}%"]
            })

            if not existing_return_stock_entry:
                self.create_return_stock_entries()




    def validate_recieved_by(self):
        '''
            Method triggered after the document is updated.
            It checks if the workflow state has changed from "Transferred" to "Transferred and Received".
        '''
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.workflow_state == "Transferred" and self.workflow_state == "Transferred and Received":
            if not self.received_by:
                frappe.throw(_("The Received By field must be filled."))

    def create_asset_movement(self):
        '''Create Asset Movement when the workflow state is 'Transferred'.'''
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
        '''Create Stock Entry when the workflow state is 'Transferred'.'''
        if not self.asset_type == "Bundle":
            return

        if not self.items:
            return

        warehouse = frappe.db.get_value("Beams Admin Settings", None, "asset_transfer_warehouse")

        if not warehouse:
            frappe.throw(_("Could not find asset_transfer_warehouse in Beams Admin Settings."))

        stock_entry = frappe.new_doc('Stock Entry')
        stock_entry.stock_entry_type = 'Material Issue'
        stock_entry.purpose = 'Material Issue'
        stock_entry.from_warehouse = warehouse
        stock_entry.posting_time = self.posting_time
        stock_entry.set("set_posting_time", 1)
        stock_entry.posting_date = self.posting_date
        stock_entry.set("set_posting_time", 1)

        for item in self.items:
            if item.item:
                stock_entry.append('items', {
                    "item_code": item.item,
                    "qty": item.qty,
                    "s_warehouse": warehouse,
                })

        if not stock_entry.items:
            frappe.throw(_("No items found to add to Stock Entry."))

        stock_entry.insert()
        stock_entry.submit()

        self.db_set("stock_entry", stock_entry.name)

        frappe.msgprint(
            _('Stock Entry Created: <a href="{0}">{1}</a>').format(get_url_to_form(stock_entry.doctype, stock_entry.name),stock_entry.name),
            alert=True, indicator='green')

    def get_valid_previous_movement_row(self, asset_name, current_location):
        """
            fetches the most recent asset movement row with full location details
            (room, shelf, row, bin) before the current location
        """
        rows = frappe.get_all(
            "Asset Movement Item",
            filters={"asset": asset_name, "docstatus": 1},
            fields=["asset", "parent", "source_location", "target_location", "room", "shelf", "row", "bin", "modified"],
            order_by="modified desc"
        )
        for row in rows:
            if row.target_location == current_location:
                continue
            if all([row.room, row.shelf, row.row, row.bin]):
                return row
        return None

    def create_asset_movement_on_return(self):
        """
            asset movement to return the asset to its previous location
            when the workflow state is set to "Returned"
        """
        asset_movement = frappe.new_doc('Asset Movement')
        asset_movement.purpose = 'Transfer'
        asset_movement.posting_time = self.posting_time
        asset_movement.reference_doctype = "Asset Transfer Request"
        asset_movement.reference_name = self.name
        asset_movement.transaction_date = datetime.strptime(f"{self.posting_date} {self.posting_time}", "%Y-%m-%d %H:%M:%S")

        added_assets = False

        if self.asset_type == "Single Asset" and self.asset:
            asset_doc = frappe.get_doc("Asset", self.asset)
            prev_row = self.get_valid_previous_movement_row(self.asset, asset_doc.location)
            if prev_row and asset_doc.location != prev_row.target_location:
                asset_movement.append('assets', {
                    "asset": self.asset,
                    "source_location": asset_doc.location,
                    "target_location": prev_row.target_location,
                    "room": prev_row.room,
                    "shelf": prev_row.shelf,
                    "row": prev_row.row,
                    "bin": prev_row.bin
                })
                added_assets = True

        elif self.asset_type == "Bundle":
            for item in self.assets:
                if item.asset:
                    asset_doc = frappe.get_doc("Asset", item.asset)
                    prev_row = self.get_valid_previous_movement_row(item.asset, asset_doc.location)
                    if prev_row and asset_doc.location != prev_row.target_location:
                        asset_movement.append('assets', {
                            "asset": item.asset,
                            "source_location": asset_doc.location,
                            "target_location": prev_row.target_location,
                            "room": prev_row.room,
                            "shelf": prev_row.shelf,
                            "row": prev_row.row,
                            "bin": prev_row.bin
                        })
                        added_assets = True

        if added_assets:
            asset_movement.insert()
            asset_movement.submit()
            frappe.msgprint(
                _('Asset Return Movement Created: <a href="{0}">{1}</a>').format(
                    get_url_to_form(asset_movement.doctype, asset_movement.name),
                    asset_movement.name
                ),
                alert=True, indicator='green'
            )

    def create_return_stock_entries(self):
        '''
            Create Stock Entry when the workflow state is 'Returned'.
        '''

        if not self.asset_type == "Bundle":
            return
        if not self.items:
            return

        items_to_return = []

        consumed_or_missing_items = set()
        if hasattr(self, 'asset_return_checklist') and self.asset_return_checklist:
            for checklist_item in self.asset_return_checklist:
                if checklist_item.consumed == 1 or checklist_item.missinglost == 1:
                    consumed_or_missing_items.add(checklist_item.checklist_item)

        for item in self.items:
            if item.item and item.item not in consumed_or_missing_items:
                items_to_return.append(item)

        if not items_to_return:
            return

        warehouse = frappe.db.get_value("Beams Admin Settings", None, "asset_transfer_warehouse")
        if not warehouse:
            frappe.throw(_("Could not find asset_transfer_warehouse in Beams Admin Settings."))

        stock_entry = frappe.new_doc('Stock Entry')
        stock_entry.stock_entry_type = 'Material Receipt'
        stock_entry.purpose = 'Material Receipt'
        stock_entry.to_warehouse = warehouse
        stock_entry.posting_time = self.posting_time
        stock_entry.set("set_posting_time", 1)
        stock_entry.posting_date = self.posting_date
        stock_entry.set("set_posting_time", 1)
        stock_entry.remarks = f"Return Stock Entry for Asset Transfer Request: {self.name}"

        for item in items_to_return:
            stock_entry.append('items', {
                "item_code": item.item,
                "qty": item.qty,
                "t_warehouse": warehouse,
            })

        if not stock_entry.items:
            frappe.throw(_("No items found to add to Return Stock Entry."))

        stock_entry.insert()
        stock_entry.submit()

        frappe.msgprint(
            _('Return Stock Entry Created: <a href="{0}">{1}</a>').format(get_url_to_form(stock_entry.doctype, stock_entry.name), stock_entry.name),
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
def get_bundle_assets(bundle):
    if not bundle:
        return {"assets": [], "bundles": []}

    bundle_doc = frappe.get_doc("Asset Bundle", bundle)
    assets_list = bundle_doc.assets if bundle_doc.assets else []
    bundles_list = bundle_doc.bundles if bundle_doc.bundles else []

    return {"assets": assets_list, "bundles": bundles_list}
