import frappe
from frappe import _

def before_save(doc, method):
    """
    Validate that the rounded total of the Purchase Invoice matches the linked Quotation before saving.
    """
    validate_purchase_invoice(doc, method)

def validate_purchase_invoice(doc, method):
    """
    Checks if the rounded total of the Purchase Invoice matches the rounded total of the linked Quotation.
    """
    if doc.quotation:  # assuming you have a field that links the Purchase Invoice to a Quotation
        quotation = frappe.get_doc('Quotation', doc.quotation)

        if doc.rounded_total != quotation.rounded_total:
            frappe.throw(_("The total amount of the Purchase Invoice does not match the Quotation amount. Please check and try again."))
