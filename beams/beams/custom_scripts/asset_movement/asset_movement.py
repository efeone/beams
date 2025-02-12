import frappe

def update_issued_quantity(doc, method):
    """ Update Issued Quantity in Equipment Request's Required Items Detail child table """

    # Ensure reference doctype is "Equipment Request"
    if doc.reference_doctype != "Required Items Detail":
        return

    if not frappe.db.exists("Required Items Detail", doc.reference_name):
        frappe.throw("Referenced Required Items Detail Not Found")

    issued_qty = frappe.db.get_value("Required Items Detail", doc.reference_name, "issued_quantity") or 0
    frappe.db.set_value("Required Items Detail", doc.reference_name, "issued_quantity", issued_qty + 1)
