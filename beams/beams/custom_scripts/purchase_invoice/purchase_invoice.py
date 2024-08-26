import frappe
from frappe import _

def before_save(doc, method):
    """
    Validate that the rounded total of the Purchase Invoice matches the linked Quotation before saving,
    but only if the 'Equalize Purchase and Sales Amounts' checkbox is checked in Beams Accounts Settings.
    """
    validate_purchase_invoice(doc)

def validate_purchase_invoice(doc):
    """
    Checks if the rounded total of the Purchase Invoice matches the rounded total of the linked Quotation
    only if the 'Equalize Purchase and Sales Amounts' checkbox is checked.
    """
    # Fetch the Beams Accounts Settings
    beams_accounts_settings = frappe.get_single('Beams Accounts Settings')

    # Check if the checkbox is enabled
    if beams_accounts_settings.equalize_purchase_and_quotation_amounts:
        if doc.quotation:  # assuming you have a field that links the Purchase Invoice to a Quotation
            quotation = frappe.get_doc('Quotation', doc.quotation)

            # Compare the rounded totals
            if doc.rounded_total != quotation.rounded_total:
                frappe.throw(_("The total amount of the Purchase Invoice does not match the Quotation amount. Please check and try again."))
