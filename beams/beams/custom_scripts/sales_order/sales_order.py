import frappe
from frappe.utils import nowdate
from frappe.model.naming import make_autoname
from beams.beams.custom_scripts.quotation.quotation import create_common_party_and_supplier
from datetime import datetime
from frappe import _

def autoname(doc, method=None):
    """Automatically generate a name for the Sales Order document based on custom naming rules defined
    in the 'Beams Accounts Settings' doctype."""
    beams_accounts_settings = frappe.get_doc("Beams Accounts Settings")
    sales_order_naming_series = ''

    # Iterate through the naming rules
    for rule in beams_accounts_settings.beams_naming_rule:
        # Check if the rule applies to the "Quotation" doctype
        if rule.doc_type == "Sales Order" and rule.naming_series:
            sales_order_naming_series = rule.naming_series
            if sales_order_naming_series:
            # Replace date placeholders with current date values
                if "{MM}" in sales_order_naming_series or "{DD}" in sales_order_naming_series or "{YY}" in sales_order_naming_series:
                    sales_order_naming_series = sales_order_naming_series.replace("{MM}", datetime.now().strftime("%m"))
                    sales_order_naming_series = sales_order_naming_series.replace("{DD}", datetime.now().strftime("%d"))
                    sales_order_naming_series = sales_order_naming_series.replace("{YY}", datetime.now().strftime("%y"))

                # Generate the name using the updated naming series
                doc.name = frappe.model.naming.make_autoname(sales_order_naming_series )
            else:
                frappe.throw(_("No valid naming series found for Sales Order doctype"))

@frappe.whitelist()
def validate_sales_order_amount_with_quotation(doc, method):
    '''
    Method to validate the sum of total amount in Sales Order against the total amount in the Quotation.
    Also checks if the `is_barter` checkbox is checked and ensures that a corresponding Purchase Invoice exists with the same customer.
    Creates common party and supplier if necessary.
    '''

    if doc.reference_id:
        # Fetch the Quotation document
        quotation = frappe.get_doc('Quotation', doc.reference_id)

        # Fetch the Beams Account Settings to check if single_sales_Order is enabled
        single_sales_order_enabled = frappe.db.get_single_value('Beams Accounts Settings', 'single_sales_order')

        # Proceed only if the single_sales_Order checkbox is checked
        if single_sales_order_enabled == 1:
            # Fetch all related Sales Invoices (excluding the current one)
            sales_orders = frappe.get_all('Sales Order',
                filters={'reference_id': doc.reference_id, 'docstatus': 1, 'name': ['!=', doc.name]},
                fields=['grand_total'])

            # Calculate the total grand total of existing Sales Invoices
            total_grand_total = sum(invoice.grand_total for invoice in sales_orders)

            # Add the current Sales Invoice's grand total
            total_grand_total += doc.grand_total

            # Perform the comparison with the Quotation's grand total
            if total_grand_total > quotation.grand_total:
                frappe.throw(_(
                    "The total amount of Sales Orders for this Quotation cannot exceed the total amount in the Quotation."
                ))

            # Optional: Inform the user if the total is less than the Quotation (if required)
            elif total_grand_total < quotation.grand_total:
                frappe.throw(_(
                    "The total amount of Sales Orders for this Quotation is less than the total amount in the Quotation."
                ))


        # Check if `is_barter` is checked in the Quotation
        if quotation.is_barter:
            # Check if there is a Purchase Invoice for the same Quotation
            purchase_invoices = frappe.get_all('Purchase Invoice',
                filters={'quotation': doc.reference_id, 'docstatus': 1},
                fields=['supplier'])

            if purchase_invoices:
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

@frappe.whitelist()
def check_overdue_invoices(customer):
    # Fetch overdue sales invoices for the given customer
    overdue_invoices = frappe.get_all('Sales Invoice',
        filters={
            'customer': customer,
            'status': 'Overdue',
            'docstatus': 1  # Only submitted invoices
        },
        fields=['name', 'due_date'])

    return overdue_invoices

def set_region_from_quotation(doc, method):
    if doc.reference_id:
        quotation = frappe.get_doc("Quotation", doc.reference_id)
        doc.region = quotation.region
