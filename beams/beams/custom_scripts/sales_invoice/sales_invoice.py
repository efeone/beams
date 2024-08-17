import frappe
from frappe import _
from beams.beams.custom_scripts.quotation.quotation import create_common_party_and_supplier

@frappe.whitelist()
def validate_sales_invoice_amount_with_quotation(doc, method):
    '''
    Method to validate the sum of total amount in Sales Invoices against the total amount in the Quotation.
    Also checks if the `is_barter` checkbox is checked and ensures that a corresponding Purchase Invoice exists with the same customer.
    Creates common party and supplier if necessary.
    '''

    if doc.reference_id:
        # Fetch the Quotation document
        quotation = frappe.get_doc('Quotation', doc.reference_id)

        # Validate the sum of Sales Invoice amounts against the Quotation
        sales_invoices = frappe.get_all('Sales Invoice',
            filters={'reference_id': doc.reference_id, 'docstatus': 1},  # Only consider submitted invoices
            fields=['grand_total'])

        total_grand_total = 0

        if sales_invoices:
            for invoice in sales_invoices:
                grand_total = invoice.grand_total
                total_grand_total += grand_total
                if total_grand_total > quotation.grand_total:
                    frappe.throw(_(
                        "The total amount of Sales Invoices for this Quotation cannot exceed the total amount in the Quotation."
                    ))

        # Check if `is_barter` is checked in the Quotation
        if quotation.is_barter:
            # Check if there is a Purchase Invoice for the same Quotation
            purchase_invoices = frappe.get_all('Purchase Invoice',
                filters={'quotation': doc.reference_id, 'docstatus': 1},
                fields=['supplier'])

            if purchase_invoices:
                # Ensure the customer exists in the Purchase Invoice
                customer = doc.customer
                for purchase_invoice in purchase_invoices:
                    supplier = purchase_invoice.supplier
                    if customer:
                        # Ensure common party accounting is enabled
                        if frappe.db.get_single_value("Accounts Settings", "enable_common_party_accounting"):
                            common_party = create_common_party_and_supplier(customer)
                            if common_party:
                                frappe.msgprint(f'Common Party and Supplier {common_party} created and linked.', indicator="green", alert=1)
            else:
                frappe.throw(_(
                    "No Purchase Invoice found for the Quotation."
                ))
