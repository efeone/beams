import os
import click
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    create_custom_fields(get_customer_custom_fields(), ignore_validate=True)
    create_custom_fields(get_sales_invoice_custom_fields(), ignore_validate=True)
    create_custom_fields(get_quotation_custom_fields(), ignore_validate=True)
    create_custom_fields(get_purchase_invoice_custom_fields(), ignore_validate=True)
    create_custom_fields(get_supplier_custom_fields(), ignore_validate=True)
    create_custom_fields(get_item_custom_fields(), ignore_validate=True)
    create_custom_fields(get_driver_custom_fields(), ignore_validate=True)
    create_custom_fields(get_employee_custom_fields(), ignore_validate=True)
    create_custom_fields(get_purchase_order_custom_fields(),ignore_validate=True)
    create_property_setters(get_property_setters())
    create_custom_fields(get_material_request_custom_fields(), ignore_validate=True)
    create_custom_fields(get_sales_order_custom_fields(), ignore_validate=True)
    create_custom_fields(get_employee_advance_custom_fields(), ignore_validate=True)
    create_custom_fields(get_journal_entry_custom_fields(), ignore_validate=True)
    create_custom_fields(get_voucher_entry_custom_fields(), ignore_validate=True)
    create_custom_fields(get_contract_custom_fields(),ignore_validate=True)
    create_custom_fields(get_department_custom_fields(),ignore_validate=True)
    create_custom_fields(get_job_requisition_custom_fields(),ignore_validate=True)
    create_custom_fields(get_quotation_item_custom_fields(),ignore_validate=True)
    create_custom_fields(get_job_opening_custom_fields(),ignore_validate=True)
    # create_custom_roles('')

def after_migrate():
    after_install()

def before_uninstall():
    delete_custom_fields(get_customer_custom_fields())
    delete_custom_fields(get_sales_invoice_custom_fields())
    delete_custom_fields(get_quotation_custom_fields())
    delete_custom_fields(get_purchase_invoice_custom_fields())
    delete_custom_fields(get_supplier_custom_fields())
    delete_custom_fields(get_item_custom_fields())
    delete_custom_fields(get_purchase_order_custom_fields())
    delete_custom_fields(get_driver_custom_fields())
    delete_custom_fields(get_material_request_custom_fields())
    delete_custom_fields(get_sales_order_custom_fields())
    delete_custom_fields(get_employee_advance_custom_fields())
    delete_custom_fields(get_employee_custom_fields())
    delete_custom_fields(get_journal_entry_custom_fields())
    delete_custom_fields(get_voucher_entry_custom_fields())
    delete_custom_fields(get_contract_custom_fields())
    delete_custom_fields(get_department_custom_fields())
    delete_custom_fields(get_job_requisition_custom_fields())
    delete_custom_fields(get_quotation_item_custom_fields())
    delete_custom_fields(get_job_opening_custom_fields())



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
                "fieldname": "albatross_customer_id",
                "fieldtype": "Data",
                "label": "Albatross Customer ID",
                "insert_after": "is_agent"
            }

        ]
    }


def get_department_custom_fields():
    '''
    Custom fields that need to be added to the Department Doctype
    '''
    return {
        "Department": [
            {
                "fieldname": "head_of_department",
                "fieldtype": "Link",
                "label": "Head Of Department",
                "options":"Employee",
                "insert_after": "department_name"
            },
            {
                "fieldname": "abbreviation",
                "fieldtype": "Data",
                "label": "Abbreviation",
                "reqd":1,
                "unique":1,
                "insert_after": "head_of_department"
            }

        ]
    }


def get_driver_custom_fields():
    '''
    Custom fields that need to be added to the Driver DocType
    '''
    return {
        "Driver": [
            {
                "fieldname": "is_internal",
                "fieldtype": "Check",
                "label": "Is Internal",
                "insert_after": "transporter",
                "reqd": 0
            }
        ]
    }

def get_purchase_order_custom_fields():
    '''
    Custom fields that need to be added to the Purchase Order DocType
    '''
    return {
        "Purchase Order": [
            {
                "fieldname": "is_budget_exceed",
                "fieldtype": "Check",
                "label": "Is Budget Exceed",
                "insert_after": "items_section",
                "read_only":1,
                "no_copy":1,
                "depends_on": "eval:doc.is_budget_exceed == 1"

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
                "depends_on": "eval:doc.is_agent == 1",
                "insert_after": "is_agent"
            },
            {
                "fieldname": "is_agent",
                "fieldtype": "Check",
                "label": "Is Agent",
                "read_only":1,
                "fetch_from": "customer.is_agent",
                "depends_on": "eval:doc.is_agent",
                "insert_after": "customer"
            },
            {
                "fieldname": "actual_customer_group",
                "fieldtype": "Link",
                "label": "Actual Customer Group",
                "options": "Customer Group",
                "read_only": 1,
                "fetch_from": "actual_customer.customer_group",
                "insert_after": "actual_customer"
            },
            {
                "fieldname": "include_in_ibf",
                "fieldtype": "Check",
                "label": "Include in IBF",
                "read_only": 1,
                "insert_after": "actual_customer_group"
            },
            {
                "fieldname": "is_barter_invoice",
                "fieldtype": "Check",
                "label": "Is Barter Invoice",
                "read_only": 1,
                "insert_after": "include_in_ibf",
                "fetch_from": "reference_id.is_barter"
            },
            {
                "fieldname": "reference_id",
                "fieldtype": "Link",
                "options":"Quotation",
                "label": "Quotation",
                "read_only":1,
                "insert_after": "naming_series"
            },
            {
                "fieldname": "sales_type",
                "fieldtype": "Link",
                "label": "Sales Type",
                "insert_after": "naming_series",
                "options": "Sales Type"
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
                "fieldname": "customer_purchase_order_reference",
                "fieldtype": "Data",
                "label": "Customer Purchase Order Reference",
                "insert_after": "valid_till"
            },
            {
                "fieldname": "is_barter",
                "fieldtype": "Check",
                "label": "Is Barter",
                "insert_after": "sales_type"
            },
            {
                "fieldname": "sales_type",
                "fieldtype": "Link",
                "label": "Default Sales Type",
                "insert_after": "order_type",
                "options": "Sales Type"
            },
            {
                "fieldname": "purchase_order",
                "fieldtype": "Link",
                "label": "Purchase Order",
                "insert_after": "valid_till",
                "depends_on": "eval:doc.is_barter",
                "options": "Purchase Order"
            },
            {
                "fieldname": "region",
                "fieldtype": "Link",
                "label": "Region",
                "insert_after": "party_name",
                "options": "Region"

            },
            {
                "fieldname": "albatross_details_section",
                "fieldtype": "Section Break",
                "label": "Albatross Details",
                "insert_after": "is_barter"
            },
            {
                "fieldname": "albatross_ro_id",
                "fieldtype": "Data",
                "label": "Albatross RO ID",
                "insert_after": "albatross_details_section"
            },
            {
                "fieldname": "albatross_invoice_number",
                "fieldtype": "Data",
                "label": "Albatross Invoice Number",
                "insert_after": "albatross_ro_id"
            },
            {
                "fieldname": "albatross_ref_number",
                "fieldtype": "Data",
                "label": "Albatross Ref Number",
                "insert_after": "albatross_invoice_number"
            },
            {
                "fieldname": "albatross_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "albatross_ref_number"
            },
            {
                "fieldname": "client_name",
                "fieldtype": "Data",
                "label": "Client Name",
                "insert_after": "albatross_column_break"
            },
            {
                "fieldname": "executive_name",
                "fieldtype": "Data",
                "label": "Executive Name",
                "insert_after": "client_name"
            }

        ]
    }

def get_quotation_item_custom_fields():
    '''
    Custom fields that need to be added to the Quotation Item Child Table
    '''
    return {
        "Quotation Item": [
            {
                "fieldname": "sales_type",
                "fieldtype": "Link",
                "label": "Sales Type",
                "options": "Sales Type",
                "insert_after": "item_name"
           }
        ]
    }

def get_purchase_invoice_custom_fields():
    '''
    Custom fields that need to be added to the Purchase Invoice Doctype
    '''
    return {
        "Purchase Invoice": [
            {
                "fieldname": "barter_invoice",
                "fieldtype": "Check",
                "label": "Barter Invoice",
                "read_only": 1,
                "fetch_from": "quotation.is_barter",
                "insert_after": "supplier"
            },
            {
                "fieldname": "quotation",
                "fieldtype": "Link",
                "label": "Quotation",
                "read_only": 1,
                "options": "Quotation",
                "insert_after": "barter_invoice"

            },
            {
                "fieldname": "invoice_type",
                "fieldtype": "Select",
                "options": "Normal\nStringer Bill",
                "default": "Normal",
                "label": "Invoice Type",
                "insert_after": "naming_series",
                "read_only": 1
            },
            {
                "fieldname": "purchase_order_id",
                "fieldtype": "Link",
                "label": "Purchase Order",
                "options": "Purchase Order",
                "insert_after": "naming_series"
            },
            {
                "fieldname": "stringer_bill_reference",
                "fieldtype": "Link",
                "label": "Stringer Bill Reference",
                "options": "Stringer Bill",
                "depends_on": "eval:doc.invoice_type == 'Stringer Bill' ",
                "read_only": 1,
                "insert_after": "purchase_order_id"
            },
            {
                "fieldname": "batta_claim_reference",
                "fieldtype": "Link",
                "label": "Batta Claim Reference",
                "read_only": 1,
                "options": "Batta Claim",
                "insert_after": "stringer_bill_reference"
            },
            {
                "fieldname": "bureau",
                "fieldtype": "Link",
                "label": "Bureau",
                "read_only": 1,
                "options": "Bureau",
                "insert_after": "supplier"
            },
            {
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "label": "Cost Center",
                "read_only": 1,
                "options": "Cost Center",
                "insert_after": "bureau"
            }
        ]
    }

def get_supplier_custom_fields():
    '''
    Custom fields that need to be added to the Supplier Doctype
    '''
    return {
        "Supplier": [
            {
                "fieldname": "is_stringer",
                "fieldtype": "Check",
                "label": "Is Stringer",
                "insert_after": "supplier_name"
            },
            {
                "fieldname": "bureau",
                "fieldtype": "Link",
                "label": "Bureau",
                "options": "Bureau",
                "depends_on": "eval:doc.is_stringer == 1",
                "insert_after": "is_stringer"

            }
        ]
    }

def get_item_custom_fields():
    '''
    Custom fields that need to be added to the Quotation Item Doctype
    '''
    return {
        "Item": [
            {
                "fieldname": "is_production_item",
                "fieldtype": "Check",
                "label": "Is Production Item",
                "insert_after": "stock_uom"
            },
            {
                "fieldname": "sales_type",
                "fieldtype": "Link",
                "label": "Sales Type",
                "options": "Sales Type",
                "insert_after": "is_production_item"
           }

        ]
    }

def get_employee_custom_fields():
    '''
    Custom fields that need to be added to the Employee Doctype
    '''
    return {
        "Employee": [
            {
                "fieldname": "Bureau",
                "fieldtype": "Link",
                "options": "Bureau",
                "label": "Bureau",
                "insert_after": "last_name"
            },
            {
                "fieldname": "stringer_type",
                "fieldtype": "Link",
                "options": "Stringer Type",
                "label": "Stringer Type",
                "insert_after": "salutation"
            }
        ]
    }


def get_voucher_entry_custom_fields():
    '''
    Custom fields that need to be added to the Employee Doctype
    '''
    return {
        "Voucher Entry": [
            {
                "fieldname": "bureau",
                "fieldtype": "Link",
                "options": "Bureau",
                "label": "Bureau",
                "insert_after": "balance"
            }
        ]
    }

def get_job_requisition_custom_fields():
    '''
    Custom fields that need to be added to the Job Requisition Doctype
    '''
    return {
        "Job Requisition": [
            {
                "fieldname": "work_details",
                "fieldtype": "Section Break",
                "label": "Work Details",
                "insert_after": "requested_by_designation"
            },
            {
                "fieldname": "employment_type",
                "fieldtype": "Link",
                "options": "Employment Type",
                "label": "Employment Type",
                "insert_after": "work_details"
            },
            {
                "fieldname": "no_of_days_off",
                "fieldtype": "Int",
                "label": "Number of Days Off",
                "insert_after": "employment_type"
            },
            {
                "fieldname": "work_details_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "no_of_days_off"
            },
            {
                "fieldname": "travel_required",
                "fieldtype": "Check",
                "label": "Travel required for the position",
                "insert_after": "work_details_column_break"
            },
            {
                "fieldname": "is_work_shift_needed",
                "fieldtype": "Check",
                "label": "Is Shift Work Needed",
                "insert_after": "travel_required"
            },
            {
                "fieldname": "driving_license_needed",
                "fieldtype": "Check",
                "label": "Driving License Needed for this Position",
                "depends_on": "eval:doc.travel_required == 1",
                "insert_after": "is_work_shift_needed"
            },
            {
                "fieldname": "license_type",
                "fieldtype": "Select",
                "label": "License Type",
                "options": "\nLight\nHeavy\nMotor Bike",
                "depends_on": "eval:doc.driving_license_needed == 1",
                "insert_after": "driving_license_needed"
            },
            {
                "fieldname": "education",
                "fieldtype": "Section Break",
                "label": "Education and Qualification Details",
                "insert_after": "license_type"
            },
            {
                "fieldname": "min_education_qual",
                "fieldtype": "Select",
                "label": "Minimum Educational Qualification",
                "options": "\nPost Graduate Diploma in Journalism/Media\nDiploma in Media/Journalism/Communication\nUndergraduate (BA/BSc/BCom in any field)\nPost graduate (BA/BSc/BCom in any field)\nBachelor's in Journalism/Mass Communication/Media Studies\nBachelor's in Film/Television Production\nMaster's in Journalism/Mass Communication/Media Studies\nMBA/PGDM (for management roles)\nPlus Two\nSSLC\nOthers",
                "insert_after": "education"
            },
            {
                "fieldname": "education_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "min_education_qual"
            },
            {
                "fieldname": "min_experience",
                "fieldtype": "Float",
                "label": "Minimum Experience Required",
                "insert_after": "education_column_break"
            },
            {
                "fieldname": "reset_column",
                "fieldtype": "Section Break",
                "label": "",
                "insert_after": "min_experience"
            },
            {
                "fieldname": "language_proficiency",
                "fieldtype": "Table",
                "options": "Language Proficiency",
                "label": "Language Proficiency",
                "insert_after": "min_experience"
            },
            {
                "fieldname": "skill_proficiency",
                "fieldtype": "Table",
                "options": "Skill Proficiency",
                "label": "Skill Proficiency",
                "insert_after": "language_proficiency"
            },
            {
                "fieldname": "job_description_template",
                "fieldtype": "Link",
                "label": "Job Description Template",
                "options": "Job Description Template",
                "insert_after": "job_description_tab"
            }
        ]
}

def get_contract_custom_fields():
    '''
    Custom fields that need to be added to the Contract Doctype
    '''
    return {
        "Contract": [
            {
                "fieldname": "services_section",
                "fieldtype": "Section Break",
                "label": "Services",
                "insert_after": "ip_address"
            },
            {
                "fieldname": "services",
                "fieldtype": "Table",
                "options": "Services",
                "label": "Services",
                "insert_after": "services_section",
                "depends_on": "eval:doc.party_type == 'Supplier'"
            },
            {
                "fieldname": "total_amount",
                "fieldtype": "Currency",
                "label": "Total Amount",
                "insert_after": "services",
                "read_only":1,
                "no_copy":1
            }
        ]
    }

def get_job_opening_custom_fields():
    '''
    Custom fields that need to be added to the Contract Doctype
    '''
    return {
        "Job Opening": [
            {
                "fieldname": "qualification_details",
                "fieldtype": "Section Break",
                "label": "Qualification Details",
                "insert_after": "location"
            },
            {
                "fieldname": "min_education_qual",
                "fieldtype": "Select",
                "label": "Minimum Educational Qualification",
                "options": "\nPost Graduate Diploma in Journalism/Media\nDiploma in Media/Journalism/Communication\nUndergraduate (BA/BSc/BCom in any field)\nPost graduate (BA/BSc/BCom in any field)\nBachelor's in Journalism/Mass Communication/Media Studies\nBachelor's in Film/Television Production\nMaster's in Journalism/Mass Communication/Media Studies\nMBA/PGDM (for management roles)\nPlus Two\nSSLC\nOthers",
                "insert_after": "qualification_details"
            },
            {
                "fieldname": "qualification_details_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "min_education_qual"
            },
            {
                "fieldname": "min_experience",
                "fieldtype": "Float",
                "label": "Minimum Experience Required",
                "insert_after": "qualification_details_column_break"
            },
            {
                "fieldname": "job_details",
                "fieldtype": "Section Break",
                "label": "Job Details",
                "insert_after": "min_experience"
            },
            {
                "fieldname": "no_of_positions",
                "fieldtype": "Float",
                "label": "Number of Positions",
                "insert_after": "job_details"
            },
            {
                "fieldname": "expected_compensation",
                "fieldtype": "Currency",
                "label": "Expected Compensation",
                "insert_after": "no_of_positions"
            },
            {
                "fieldname": "job_details_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "expected_compensation"
            },
            {
                "fieldname": "no_of_days_off",
                "fieldtype": "Int",
                "label": "Number of Days Off",
                "insert_after": "job_details_column_break"
            }
        ]
    }

def create_property_setters(property_setter_datas):
    '''
    Method to create custom property setters
    args:
        property_setter_datas : list of dict of property setter obj
    '''
    for property_setter_data in property_setter_datas:
        if frappe.db.exists("Property Setter", property_setter_data):
            continue
        property_setter = frappe.new_doc("Property Setter")
        property_setter.update(property_setter_data)
        property_setter.flags.ignore_permissions = True
        property_setter.insert()

def get_property_setters():
    '''
        BEAMS specific property setters that need to be added to the Customer ,Account and Supplier DocTypes
    '''
    return [
        {
            "doctype_or_field": "DocField",
            "doc_type": "Customer",
            "field_name": "disabled",
            "property": "default",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Customer",
            "field_name": "disabled",
            "property": "read_only",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Account",
            "field_name": "disabled",
            "property": "default",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Account",
            "field_name": "disabled",
            "property": "read_only",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Supplier",
            "field_name": "disabled",
            "property": "default",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Supplier",
            "field_name": "disabled",
            "property": "read_only",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Advance",
            "field_name": "purpose",
            "property": "hidden",
            "property_type": "Small Text",
            "value":1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Purchase Invoice",
            "field_name": "update_stock",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Purchase Invoice",
            "field_name": "is_subcontracted",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Purchase Invoice",
            "field_name": "scan_barcode",
            "property": "hidden",
            "property_type": "Data",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Advance",
            "field_name": "naming_series",
            "property": "hidden",
            "property_type": "Data",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "posting_date",
            "property": "read_only",
            "value": 1
        },
    ]

def get_material_request_custom_fields():
    '''
    Custom fields that need to be added to the Material Request Doctype
    '''
    return {
        "Material Request": [
            {
                "fieldname": "budget_exceeded",
                "fieldtype": "Check",
                "label": "Budget Exceeded",
                "insert_after": "schedule_date",
                "read_only":1,
                "no_copy":1,
                "depends_on": "eval:doc.budget_exceeded == 1"

            }
        ]
    }

def get_sales_order_custom_fields():
    '''
    Custom fields that need to be added to the Sales Order Doctype
    '''
    return {
        "Sales Order": [
            {
                "fieldname": "sales_type",
                "fieldtype": "Link",
                "label": "Sales Type",
                "insert_after": "naming_series",
                "options": "Sales Type"
            },
            {
                "fieldname": "actual_customer",
                "fieldtype": "Link",
                "label": "Actual Customer",
                "options": "Customer",
                "depends_on": "eval:doc.is_agent == 1",
                "insert_after": "is_agent"
            },
            {
                "fieldname": "is_agent",
                "fieldtype": "Check",
                "label": "Is Agent",
                "read_only":1,
                "fetch_from": "customer.is_agent",
                "depends_on": "eval:doc.is_agent",
                "insert_after": "customer"
            },
            {
                "fieldname": "actual_customer_group",
                "fieldtype": "Link",
                "label": "Actual Customer Group",
                "options": "Customer Group",
                "read_only": 1,
                "fetch_from": "actual_customer.customer_group",
                "insert_after": "actual_customer"
            },
            {
                "fieldname": "include_in_ibf",
                "fieldtype": "Check",
                "label": "Include in IBF",
                "read_only": 1,
                "insert_after": "actual_customer_group"
            },
            {
                "fieldname": "is_barter_invoice",
                "fieldtype": "Check",
                "label": "Is Barter Invoice",
                "read_only": 1,
                "insert_after": "include_in_ibf",
                "fetch_from": "reference_id.is_barter"
            },
            {
                "fieldname": "reference_id",
                "fieldtype": "Link",
                "options":"Quotation",
                "label": "Quotation",
                "read_only":1,
                "insert_after": "naming_series"
            }
        ]
    }

def get_employee_advance_custom_fields():
    '''
    Custom fields that need to be added to the Employee Advance  Doctype
    '''
    return {
        "Employee Advance": [
            {
                "fieldname": "purpose",
                "fieldtype": "Link",
                "label": "Purpose",
                "options": "Employee Advance Purpose",
                "insert_after":"currency"
            },
            {
                "fieldname": "purpose",
                "fieldtype": "Link",
                "label": "Purpose",
                "options": "Employee Advance Purpose",
                "insert_after": "currency",
                "reqd": 1
            }

        ]
    }

def get_journal_entry_custom_fields():
    '''
    Custom fields that need to be added to the Journal Entry Doctype.
    '''
    return {
        "Journal Entry": [
            {
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "label": "Cost Center",
                "read_only": 1,
                "options": "Cost Center",
                "insert_after": "naming_series"
            },
            {
                "fieldname": "batta_claim_reference",
                "fieldtype": "Link",
                "label": "Batta Claim Reference",
                "read_only": 1,
                "options": "Batta Claim",
                "insert_after": "voucher_type"
            },
            {
                "fieldname": "substitute_booking_reference",
                "fieldtype": "Link",
                "label": "Substitute Booking Reference",
                "read_only": 1,
                "options": "Substitute Booking",
                "insert_after": "batta_claim_reference"
            }

        ]
    }


def create_custom_roles(role_name):
    """
    Method to create Role , when argument is Passed
    """

    if not frappe.db.exists("Role", role_name):
            new_role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name
            })
            new_role.insert(ignore_permissions=True)
            print(f"Created role: {role_name}")
    else:
            print(f"Role already exists: {role_name}")

    frappe.db.commit()
