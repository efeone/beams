import frappe

def update_issued_quantity(doc, method):
    """ Update Issued Quantity in Equipment Request's Required Items Detail child table """

    # Ensure reference doctype is "Equipment Request"
    if doc.reference_doctype != "Required Items Detail":
        return
    # Check if the referenced Required Items Detail exists
    if not frappe.db.exists("Required Items Detail", doc.reference_name):
        frappe.throw("Referenced Required Items Detail Not Found")

    issued_qty = frappe.db.get_value("Required Items Detail", doc.reference_name, "issued_quantity") or 0
    frappe.db.set_value("Required Items Detail", doc.reference_name, "issued_quantity", issued_qty + 1)

def before_save(doc, method):
    if doc.assets:
        first_asset = doc.assets[0]
        if first_asset.to_employee:
            doc.new_custodian = first_asset.to_employee

            new_custodian_doc = frappe.get_doc("Employee", doc.new_custodian)
            if new_custodian_doc.user_id:
                doc.user_id = new_custodian_doc.user_id
