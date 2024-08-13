import frappe
from frappe import _

def validate_sales_invoice(doc, method):
    """
    Validates the Sales Invoice to ensure that the rounded total does not exceed the expected amounts.
    """

    # Get the expected_total value, ensuring it is not None
    expected_total = doc.get('expected_total') or 0.0

    # Ensure rounded_total is also not None (though it should generally have a value)
    rounded_total = doc.rounded_total or 0.0
    if rounded_total > expected_total:
        frappe.throw(_("The Sales Invoice amount exceeds the expected total from the Quotation.").format(rounded_total, expected_total))
