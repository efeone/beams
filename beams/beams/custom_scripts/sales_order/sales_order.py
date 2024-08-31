import frappe
from frappe.utils import nowdate
from frappe.model.naming import make_autoname
from datetime import datetime
from frappe import _

def autoname(doc, method=None):
    beams_accounts_settings = frappe.get_doc("Beams Accounts Settings")
    sales_order_naming_series = ''

    for rule in beams_accounts_settings.beams_naming_rule:
        # Check if the rule applies to the "Quotation" doctype
        if rule.doc_type == "Sales Order" and rule.naming_series:
            sales_order_naming_series = rule.naming_series
            if sales_order_naming_series:
                if "{MM}" in sales_order_naming_series or "{DD}" in sales_order_naming_series or "{YY}" in sales_order_naming_series:
                    sales_order_naming_series = sales_order_naming_series.replace("{MM}", datetime.now().strftime("%m"))
                    sales_order_naming_series = sales_order_naming_series.replace("{DD}", datetime.now().strftime("%d"))
                    sales_order_naming_series = sales_order_naming_series.replace("{YY}", datetime.now().strftime("%y"))

                # Generate the name using the updated naming series
                doc.name = frappe.model.naming.make_autoname(sales_order_naming_series )
            else:
                frappe.throw(_("No valid naming series found for Sales Order doctype"))
