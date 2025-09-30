# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
import json

from frappe.desk.form.assign_to import add as add_assign
from frappe.model.document import Document


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
			movement.append("assets", {"asset": row["asset"], "to_employee": assigned_to})

		# Bundle
		elif row.get("bundle"):
			bundle_doc = frappe.get_doc("Asset Bundle", row["bundle"])

			# Add assets from bundle
			for asset in getattr(bundle_doc, "assets", []):
				movement.append("assets", {"asset": asset.asset, "to_employee": assigned_to})

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




