
import frappe
from frappe import _

@frappe.whitelist()
def validate_sales_invoice_amount_with_quotation(doc, method):
    '''
        Method to validate the sum of total amount in Sales Invoices against the total amount in the Quotation.
    '''

    if doc.reference_id:
        quotation = frappe.get_doc('Quotation', doc.reference_id)
        sales_invoices = frappe.get_all('Sales Invoice',
                                         filters={'reference_id': doc.reference_id, 'docstatus': 1},  # Only consider submitted invoices
                                         fields=['grand_total'])

        if sales_invoices:
            for invoice in sales_invoices:
                grand_total = invoice.grand_total
                total_grand_total = doc.grand_total + grand_total
                if total_grand_total > quotation.grand_total:
                    frappe.throw(_(
                        "The total amount of Sales Invoices for this Quotation cannot exceed the total amount in the Quotation."
                    ))
