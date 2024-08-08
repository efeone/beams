import os
import click
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    create_custom_fields(get_customer_custom_fields(), ignore_validate=True)
    create_custom_fields(get_sales_invoice_custom_fields(), ignore_validate=True)
    create_custom_fields(get_quotation_custom_fields(), ignore_validate=True)

def after_migrate():
    after_install()

def before_uninstall():
    delete_custom_fields(get_customer_custom_fields())
    delete_custom_fields(get_sales_invoice_custom_fields())
    delete_custom_fields(get_quotation_custom_fields())


def delete_custom_fields(custom_fields: dict):
    '''
    Method to Delete custom fields
    args:
        custom_fields: a dict like `{'Task': [{fieldname: 'your_fieldname', ...}]}`
    '''
    for doctype, fields in custom_fields.items():
        frappe.db.delete(
            "Custom Field",
            {
                "fieldname": ("in", [field["fieldname"] for field in fields]),
                "dt": doctype,
            },
        )
        frappe.clear_cache(doctype=doctype)

def get_customer_custom_fields():
    '''
    Custom fields that need to be added to the Customer Doctype
    '''
    return {
        "Customer": [
            {
                "fieldname": "msme_status",
                "fieldtype": "Select",
                "label": "MSME Status",
                "options":"\nMSME\nNon-MSME",
                "insert_after": "customer_group"
            },
            {
                "fieldname": "is_agent",
                "fieldtype": "Check",
                "label": "Is Agent",
                "insert_after": "msme_status"
            },
            {
                "fieldname": "agent_of",
                "fieldtype": "Link",
                "label": "Agent Of",
                "options": "Customer",
                "depends_on": "eval:doc.is_agent == 1",
                "insert_after": "is_agent"
            }

        ]
    }

def get_sales_invoice_custom_fields():
    '''
    Custom fields that need to be added to the Sales Invoice Doctype
    '''
    return {
        "Sales Invoice": [
            {
                "fieldname": "actual_customer",
                "fieldtype": "Link",
                "label": "Actual Customer",
                "options": "Customer",
                "insert_after": "customer"
            },
            {
                "fieldname": "actual_customer_group",
                "fieldtype": "Link",
                "label": "Actual Customer Group",
                "options": "Customer Group",
                "insert_after": "actual_customer"
            },
            {
                "fieldname": "include_in_ibf",
                "fieldtype": "Check",
                "label": "Include in IBF",
                "insert_after": "actual_customer_group"
            },
            {
                "fieldname": "is_barter_invoice",
                "fieldtype": "Check",
                "label": "Is Barter Invoice",
                "insert_after": "include_in_ibf"
            }
        ]
    }

def get_quotation_custom_fields():
    '''
    Custom fields that need to be added to the Quotation DocType
    '''
    return {
        "Quotation": [
            {
                "fieldname": "customer_purchase_reference_id",
                "fieldtype": "Data",
                "label": "Customer Purchase Reference ID",
                "insert_after": "valid_till"
            },
            {
                "fieldname": "is_barter",
                "fieldtype": "Check",
                "label": "Is Barter",
                "insert_after": "order_type"
            }
        ]
    }
