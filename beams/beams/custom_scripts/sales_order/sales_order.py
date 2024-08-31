import frappe
from frappe.utils import nowdate
from frappe.model.naming import make_autoname
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
