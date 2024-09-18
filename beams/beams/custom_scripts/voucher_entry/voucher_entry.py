import frappe
from frappe import _
from frappe.utils import get_link_to_form

@frappe.whitelist()
def get_default_account(voucher_entry_type, company):
    """
    Retrieve the default account for a given Voucher Entry Type and company.
    Args:
        voucher_entry_type (str): Name of the Voucher Entry Type.
        company (str): Name of the company.
    Returns:
        str: The default account associated with the Voucher Entry Type and company.
    """
    default_account = frappe.db.get_value('Accounts',{'parent': voucher_entry_type, 'parenttype': 'Voucher Entry Type', 'company': company}, 'default_account')
    return default_account

@frappe.whitelist()
def validate_company_for_voucher_entry_type(voucher_entry_type, company):
    """
    Validate if the specified company is associated with the given Voucher Entry Type.
    If the company is not valid, raise a validation error.
    Args:
        voucher_entry_type (str): Name of the Voucher Entry Type.
        company (str): Name of the company.
    Raises:
        frappe.ValidationError: If the company is not associated with the Voucher Entry Type.
    Returns:
        bool: True if the company is valid for the Voucher Entry Type.
    """
    entry_type = frappe.get_doc('Voucher Entry Type', voucher_entry_type)
    valid_companies = [account.company for account in entry_type.accounts]
    if company not in valid_companies:
        frappe.throw(
            _("Set the default account for the {0} {1}").format(
                frappe.bold("Voucher Entry Type\t"),
                get_link_to_form("Voucher Entry Type", voucher_entry_type)
            )
        )
    return True
