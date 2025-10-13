import frappe
from frappe.utils import flt

def update_issued_quantity(doc, method):
	"""
	Updates Issued Quantity in 'Required Items Detail' of an Equipment Request,
	and updates or inserts corresponding rows in Project's Allocated Item Details,
	based on the Asset Movement.
	"""
	if not doc.assets:
		frappe.throw("No assets found in this Asset Movement.")

	reference_name = doc.reference_name
	if not reference_name:
		return

	required_items = frappe.get_all(
		"Required Items Detail",
		filters={"parent": reference_name},
		fields=["name", "required_item", "issued_quantity", "required_quantity"]
	)

	if not required_items:
		return

	asset_count = {}
	for asset in doc.assets:
		if not asset.asset_name:
			frappe.throw(f"Asset Name not set for Asset {asset.asset}.")
		asset_count[asset.asset_name] = asset_count.get(asset.asset_name, 0) + 1

	for req in required_items:
		item = req.required_item
		if item in asset_count:
			new_issued_qty = (req.issued_quantity or 0) + asset_count[item]
			frappe.db.set_value("Required Items Detail", req.name, "issued_quantity", new_issued_qty)

	project_name = frappe.db.get_value("Equipment Request", reference_name, "project")
	if not project_name:
		return

	project_doc = frappe.get_doc("Project", project_name)

	for req in required_items:
		item = req.required_item
		if item in asset_count:
			for row in project_doc.allocated_item_details:
				if row.required_item == item:
					row.issued_quantity = (row.issued_quantity or 0) + asset_count[item]
					break
			else:
				project_doc.append("allocated_item_details", {
					"required_item": item,
					"required_quantity": req.required_quantity,
					"issued_quantity": asset_count[item],
				})

	project_doc.save(ignore_permissions=True)

def before_save(doc, method):
	if doc.assets:
		first_asset = doc.assets[0]
		if first_asset.to_employee:
			doc.new_custodian = first_asset.to_employee

			new_custodian_doc = frappe.get_doc("Employee", doc.new_custodian)
			if new_custodian_doc.user_id:
				doc.user_id = new_custodian_doc.user_id

@frappe.whitelist()
def update_asset_location_from_movement(doc, method=None):
	"""
		Updates the location and physical storage details (room, shelf, row, bin)
		of assets listed in an Asset Movement document.
		If any of these fields are empty in the movement record, they will also be cleared in the Asset.
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("Asset Movement", doc)

	for item in doc.assets:
		if not item.asset:
			continue

		asset = frappe.get_doc("Asset", item.asset)
		updated = False

		if item.department:
			asset.department = item.department
			updated = True

		if item.target_location:
			asset.location = item.target_location
			updated = True
		else:
			return

		for field in ["room", "shelf", "row", "bin"]:
			item_value = getattr(item, field, None)
			setattr(asset, field, item_value if item_value is not None else "")
			updated = True

		if updated:
			asset.save(ignore_permissions=True)


def update_allocated_asset_details(doc, method=None):
	"""Update Asset Request with Asset Movement Item details when Asset Movement is submitted."""

	if doc.reference_doctype != "Asset Request" or not doc.reference_name:
		return

	if doc.purpose == "Issue":

		asset_request = frappe.get_doc("Asset Request", doc.reference_name)

		asset_request.asset_movement_items = []

		for asset_row in doc.assets:
			new_row = asset_request.append("allocated_assets", {})

			new_row.company = asset_row.company
			new_row.asset = asset_row.asset
			new_row.asset_name = asset_row.asset_name
			new_row.source_location = asset_row.source_location
			new_row.target_location = asset_row.target_location
			new_row.from_employee = asset_row.from_employee
			new_row.to_employee = asset_row.to_employee
			new_row.department = asset_row.department
			new_row.room = asset_row.room
			new_row.row = asset_row.row
			new_row.shelf = asset_row.shelf
			new_row.bin = asset_row.bin

		asset_request.save(ignore_permissions=True)



def update_asset_custodian_on_receipt(doc, method=None):

	"""Clears the Asset custodian when an Asset Movement with purpose 'Receipt' is submitted and no new employee is assigned."""

	if doc.purpose == "Receipt" and doc.reference_doctype == "Asset Request":
		for asset_row in doc.assets:
			if asset_row.asset and not asset_row.to_employee:
				frappe.db.set_value("Asset", asset_row.asset, "custodian", None)
