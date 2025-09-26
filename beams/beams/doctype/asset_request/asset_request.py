# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class AssetRequest(Document):
	pass
	
	

@frappe.whitelist()
def create_asset_movement(assigned_to, purpose, items, reference_name=None):
	"""
	Create a Asset Movement document with child rows
	for all selected assets
	"""
	if isinstance(items, str):
		items = json.loads(items)

	if not items:
		frappe.throw("No items provided for asset assignment")

	movement = frappe.new_doc("Asset Movement")
	movement.purpose = purpose
	movement.to_employee = assigned_to
	movement.transaction_date = frappe.utils.nowdate()
	movement.reference_doctype = "Asset Request"
	movement.reference_name = reference_name


	for row in items:
		if not row.get("asset"):
			continue
		movement.append("assets", {
			"asset": row["asset"],
			"to_employee": assigned_to
		})

	if not movement.assets:
		frappe.throw("No valid assets selected for assignment")

	movement.insert(ignore_permissions=True)

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
                    issued_count[item_code] += 1

    # Update the child table
    for row in request.items:
        row.issued_quantity = issued_count.get(row.item_code, 0)

    request.save(ignore_permissions=True)
