import frappe
from frappe import _

@frappe.whitelist()
def validate_repeating_companies(doc, method=None):
    """Error when the same Company is entered multiple times in accounts"""
    companies = [entry.company for entry in doc.accounts]

    if len(companies) != len(set(companies)):
        frappe.throw(
            _("Same Company is entered multiple times in Accounts"), 
            title=_("Duplicate Company Entry")
        )
