import frappe
from frappe import _
def validate_purchase_invoice(doc, method):
    if doc.quotation:  # assuming you have a field that links the Purchase Invoice to a Quotation
        quotation = frappe.get_doc('Quotation', doc.quotation)

        if doc.rounded_total != quotation.rounded_total:
            frappe.throw(_("The rounded total amount of the Purchase Invoice does not match the Quotation amount. Please check and try again."))

def before_save(doc, method):
    validate_purchase_invoice(doc, method)
