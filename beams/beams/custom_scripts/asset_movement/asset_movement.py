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
        frappe.throw("Reference name missing in Asset Movement.")

    required_items = frappe.get_all(
        "Required Items Detail",
        filters={"parent": reference_name},
        fields=["name", "required_item", "issued_quantity", "required_quantity"]
    )

    if not required_items:
        frappe.throw(f"No Required Items found for Equipment Request {reference_name}.")

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
        frappe.throw(f"Project not linked in Equipment Request {reference_name}.")

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
