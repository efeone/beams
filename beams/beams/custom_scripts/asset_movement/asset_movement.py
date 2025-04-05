import frappe
from frappe.utils import flt

def update_issued_quantity(doc, method):
    """
    Update or insert Issued Quantity in Project's Allocated Item Details table
    based on Equipment Request, using reference from Asset Movement.
    """

    # Validate the reference
    if not frappe.db.exists("Required Items Detail", doc.reference_name):
        return

    # Get existing issued quantity and increment by quantity moved (default = 1)
    movement_qty = flt(getattr(doc, "quantity", 1))
    existing_issued = flt(frappe.db.get_value("Required Items Detail", doc.reference_name, "issued_quantity")) or 0
    frappe.db.set_value("Required Items Detail", doc.reference_name, "issued_quantity", existing_issued + movement_qty)

    # Get parent Equipment Request from the child table
    equipment_request = frappe.db.get_value("Required Items Detail", doc.reference_name, "parent")
    if not equipment_request:
        return

    # Get associated project
    project_name = frappe.db.get_value("Equipment Request", equipment_request, "project")
    if not project_name:
        return

    # Get the required item from the Required Items Detail
    required_item_value = frappe.db.get_value("Required Items Detail", doc.reference_name, "required_item")
    if not required_item_value:
        return

    # Get required_quantity from the Equipment Request's child table
    eq_doc = frappe.get_doc("Equipment Request", equipment_request)
    required_quantity = 0
    for item in eq_doc.required_equipments:
        if item.required_item == required_item_value:
            required_quantity = flt(item.required_quantity or 0)
            break

    # Update the Project's allocated_item_details table
    if frappe.db.exists("Project", project_name):
        project_doc = frappe.get_doc("Project", project_name)
        found = False

        for row in project_doc.allocated_item_details:
            if row.required_item == required_item_value:
                row.issued_quantity = flt(row.issued_quantity or 0) + movement_qty
                found = True
                break

        if not found:
            project_doc.append("allocated_item_details", {
                "required_item": required_item_value,
                "required_quantity": required_quantity,
                "issued_quantity": movement_qty,
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
