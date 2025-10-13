# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
import json

from frappe.desk.form.assign_to import add as add_assign
from frappe.model.document import Document
from frappe import _


class AssetRequest(Document):
	def on_update(self):
		self.assign_asset_manager()

	def assign_asset_manager(self):
		"""
        Assigns the document to the appropriate Asset Manager based on the item type.
        """
		if self.workflow_state == "Sent to Asset Manager":
			if self.item_type == "Technical Item":
				asset_manager = frappe.db.get_value("Beams Admin Settings", None, "technical_asset_manager")
			else:
				asset_manager = frappe.db.get_value("Beams Admin Settings", None, "non_technical_asset_manager")

			user_id = frappe.db.get_value("Employee", asset_manager, "user_id")

			if asset_manager:
				add_assign({
				"assign_to": [user_id],
				"doctype": self.doctype,
				"name": self.name,
				"description": f"Asset Request forwarded for {self.item_type} Asset Manager approval"
				})


@frappe.whitelist()
def create_asset_movement(assigned_to, purpose, items, reference_name=None):
	"""
	Create an Asset Movement document with child rows for assets.
	If a bundle contains stock_items, create a Stock Entry for them.
	"""
	if isinstance(items, str):
		items = json.loads(items)

	if not items:
		frappe.throw("No items provided for asset assignment")

	# Create Asset Movement
	movement = frappe.new_doc("Asset Movement")
	movement.purpose = purpose
	movement.to_employee = assigned_to
	movement.transaction_date = frappe.utils.nowdate()
	movement.reference_doctype = "Asset Request"
	movement.reference_name = reference_name

	for row in items:
		# Single Asset
		if row.get("asset"):
			source_location = frappe.db.get_value("Asset", row["asset"], "location")
			movement.append("assets", {"asset": row["asset"], "to_employee": assigned_to, "source_location": source_location})

		# Bundle
		elif row.get("bundle"):
			bundle_doc = frappe.get_doc("Asset Bundle", row["bundle"])

			# Add assets from bundle
			for asset in getattr(bundle_doc, "assets", []):
				source_location = frappe.db.get_value("Asset", asset.asset, "location")
				movement.append("assets", {"asset": asset.asset, "to_employee": assigned_to, "source_location": source_location})

			# Create Stock Entry if stock_items exist
			stock_items = getattr(bundle_doc, "stock_items", [])
			if stock_items:
				stock_entry = frappe.new_doc("Stock Entry")
				stock_entry.update({
					"purpose": "Material Issue",
					"from_warehouse": frappe.db.get_value("Beams Admin Settings", None, "asset_transfer_warehouse"),
					"to_warehouse": None,
					"reference_doctype": "Asset Request",
					"reference_name": reference_name,
					"stock_entry_type": "Material Issue"
				})

				for item in stock_items:
					stock_entry.append("items", {
						"item_code": item.item,
						"qty": item.qty,
						"uom": item.uom,
						"conversion_factor": 1,
					})

				stock_entry.insert(ignore_permissions=True)
				stock_entry.submit()

	if not movement.assets:
		frappe.throw("No valid assets selected for assignment")

	movement.insert(ignore_permissions=True)
	movement.submit()

	return {"name": movement.name}


@frappe.whitelist()
def update_issued_quantity(doc, method=None):
	"""
	Updates issued_quantity in Asset Request Item whenever an Asset Movement
	linked to an Asset Request is submitted.
	"""
	if doc.reference_doctype != "Asset Request" or not doc.reference_name:
		return

	request = frappe.get_doc("Asset Request", doc.reference_name)

	issued_count = {row.item_code: 0 for row in request.items}

	# Get all submitted Asset Movements linked to this Asset Request
	movements = frappe.get_all(
		"Asset Movement",
		filters={"reference_doctype": "Asset Request", "reference_name": request.name, "docstatus": 1},
		fields=["name"]
	)

	for mv in movements:
		for asset_row in frappe.get_doc("Asset Movement", mv.name).assets:
			if asset_row.asset:
				item_code = frappe.db.get_value("Asset", asset_row.asset, "item_code")
				if item_code:
					issued_count[item_code] = issued_count.get(item_code, 0) + 1

	for row in request.items:
		row.issued_quantity = issued_count.get(row.item_code, 0)

	request.save(ignore_permissions=True)

@frappe.whitelist()
def acknowledge_assets(asset_request_name):
    """Mark all unacknowledged assets in an Asset Request as acknowledged and notify if technical item."""
    
    asset_request = frappe.get_doc("Asset Request", asset_request_name)

    updated = False

    for asset in asset_request.allocated_assets:
        if not asset.acknowledged:
            asset.acknowledged = 1
            updated = True

    if updated:
        asset_request.save(ignore_permissions=True)

        if asset_request.item_type:
             send_mail_to_asset_manager(asset_request, asset_request.item_type)

        return _("Assets acknowledged successfully!")
    else:
        return _("All assets were already acknowledged.")


def send_mail_to_asset_manager(asset_request, item_type):
    """Send email notification to Asset Manager."""
    
    asset_settings = frappe.get_single('BEAMS Admin Settings')

    if item_type == 'Technical Item':
        manager_emp = asset_settings.get('technical_asset_manager') or ''
    elif item_type == 'Non-Technical Item':
        manager_emp = asset_settings.get('non_technical_asset_manager') or ''
    else:
        return

    manager_email = frappe.get_value("Employee", manager_emp, "user_id")
    if not manager_email:
        return

    frappe.sendmail(
        recipients=[manager_email],
        subject=f"Assets Acknowledged: {asset_request.name}",
        message=f"The assets in Asset Request {asset_request.name} have been acknowledged."
    )



@frappe.whitelist()
def mark_assets_returned(docname, assets):
    """Mark selected allocated assets as returned in Asset Request."""

    if isinstance(assets, str):
        assets = json.loads(assets)

    doc = frappe.get_doc("Asset Request", docname)

    updated = 0
    for row in doc.allocated_assets:
        if row.asset in assets:
            row.returned = 1
            updated += 1

    if updated:
        doc.save(ignore_permissions=True)

    return {"updated": updated}
