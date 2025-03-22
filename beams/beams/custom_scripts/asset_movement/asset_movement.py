import frappe

def update_issued_quantity(doc, method):
    """
    Update Issued Quantity in Equipment Request's Required Items Detail child table and Project
    """
    if frappe.db.exists("Required Items Detail", doc.reference_name):
        issued_qty = frappe.db.get_value("Required Items Detail", doc.reference_name, "issued_quantity") or 0
        frappe.db.set_value("Required Items Detail", doc.reference_name, "issued_quantity", issued_qty + 1)

        equipment_request = frappe.db.get_value("Required Items Detail", doc.reference_name, "parent")
        if equipment_request:
            project_name = frappe.db.get_value("Equipment Request", equipment_request, "project")

            if project_name and frappe.db.exists("Project", project_name):
                project_doc = frappe.get_doc("Project", project_name)
                updated = False
                required_item_value = frappe.db.get_value("Required Items Detail", doc.reference_name, "required_item")

                for item in project_doc.required_items:
                    if item.required_item == required_item_value:
                        item.issued_quantity += 1
                        updated = True

                if updated:
                    project_doc.save()

def before_save(doc, method):
    if doc.assets:
        first_asset = doc.assets[0]
        if first_asset.to_employee:
            doc.new_custodian = first_asset.to_employee

            new_custodian_doc = frappe.get_doc("Employee", doc.new_custodian)
            if new_custodian_doc.user_id:
                doc.user_id = new_custodian_doc.user_id
