
import frappe
from frappe import _

@frappe.whitelist()
def validate_sales_order_amount(doc, method):
    """
        Method to validate the grand total in  Sales Invoice and grand total in  Quotation.
    """
    if doc.reference_id:
        quotation = frappe.get_doc('Quotation', doc.reference_id)
        if doc.grand_total != quotation.grand_total:
            frappe.throw(_(
                "The total amount in the Sales Invoice must match the total amount in the Quotation."
            ))
