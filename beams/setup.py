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
    create_custom_fields(get_expected_skill_set_custom_fields(),ignore_validate=True)
    create_custom_fields(get_interview_round_custom_fields(),ignore_validate=True)
    # create_custom_roles('')
    create_custom_fields(get_job_applicant_custom_fields(),ignore_validate=True)
    create_custom_fields(get_budget_custom_fields(),ignore_validate=True)
    create_custom_fields(get_budget_account_custom_fields(),ignore_validate=True)
    create_custom_fields(get_interview_feedback_custom_fields(),ignore_validate=True)
    create_custom_fields(get_skill_assessment_custom_fields(), ignore_validate=True)

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
    delete_custom_fields(get_job_applicant_custom_field())
    delete_custom_fields(get_budget_custom_fields())
    delete_custom_fields(get_budget_account_custom_fields())
    delete_custom_fields(get_expected_skill_set_custom_fields())
    delete_custom_fields(get_interview_round_custom_fields())
    delete_custom_fields(get_skill_assessment_custom_fields())

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
                "label": "Is Agency",
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
            },
            {
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "label": "Cost Center",
                "options":"Cost Center",
                "insert_after": "company",
                "reqd":1
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

def get_budget_custom_fields():
    '''
    Custom fields that need to be added to the Budget DocType
    '''
    return {
        "Budget": [
            {
                "fieldname": "department",
                "fieldtype": "Link",
                "label": "Department",
                "options":"Department",
                "insert_after": "monthly_distribution"
            }
        ]
    }

def get_budget_account_custom_fields():
    '''
    Custom fields that need to be added to the Budget Account Child Table
    '''
    return {
        "Budget Account": [
            {
                "fieldname": "cost_subhead",
                "fieldtype": "Link",
                "label": "Cost Subhead",
                "options":"Cost Subhead",
                "insert_after": "cost_description"
            },
            {
                "fieldname": "cost_category",
                "fieldtype": "Link",
                "label": "Cost Category",
                "options":"Cost Category",
                "insert_after": "account"
            },
            {
                "fieldname": "cost_description",
                "fieldtype": "Data",
                "label": "Cost Description",
                "insert_after": "cost_category"
            },
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
                "label": "Is Agency",
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


def get_expected_skill_set_custom_fields():
    '''
    Custom fields that need to be added to the Expected Skill Set Doctype
    '''
    return {
        "Expected Skill Set": [
            {
                "fieldname": "weight",
                "fieldtype": "Float",
                "label": "Weight",
                "insert_after": "description"
            }
        ]
    }

def get_interview_round_custom_fields():
    '''
    Custom fields that need to be added to the Interview Round Child Table
    '''
    return {
        "Interview Round": [
            {
                "fieldname": "expected_question_set",
                "fieldtype": "Table",
                "label": "Expected Questions Set",
                "options":"Expected Question Set",
                "insert_after":"expected_skill_set"
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
                "description": " number of days off within a 30-day period",
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
                "fieldtype": "Link",
                "label": "License Type",
                "options": "License Type",
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
                "fieldtype": "Table MultiSelect",
                "label": "Minimum Educational Qualification",
                'options':"Educational Qualifications",
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
                "description": "Proficency selected here is the minimum proficency needed.",
                "insert_after": "language_proficiency"
            },
            {
                "fieldname": "job_description_template",
                "fieldtype": "Link",
                "label": "Job Description Template",
                "options": "Job Description Template",
                "insert_after": "job_description_tab"
            },
            {
                "fieldname": "request_for",
                "label": "Request For",
                "fieldtype": "Select",
                "options": "\nEmployee Exit\nStaffing Plan\nUnplanned",
                "insert_after": "naming_series"
            },
            {
                "fieldname": "employee_left",
                "label": "Employees Who Left",
                "fieldtype": "Table MultiSelect",
                "options": "Employees Left",
                "insert_after": "request_for",
                "depends_on": "eval:doc.request_for == 'Employee Exit'"
            },
            {
                "fieldname": "staffing_plan",
                "label": "Staffing Plan",
                "fieldtype": "Link",
                "options": "Staffing Plan",
                "insert_after": "employee_left",
                "depends_on": "eval:doc.request_for == 'Staffing Plan'"
            },
            {
                "fieldname": "requested_by",
                "label": "Requested By",
                "fieldtype": "Link",
                "options": "Employee",
                "insert_after": "staffing_plan",
            },
            {
                "fieldname": "interview",
                "fieldtype": "Section Break",
                "label": "Interview Details",
                "insert_after": "requested_by_designation"
            },
            {
                "fieldname": "interview_rounds",
                "fieldtype": "Table MultiSelect",
                "options": "Interview Rounds",
                "label": "Interview Rounds",
                "insert_after": "interview"
            },

             {
                "fieldname": "location",
                "label": "Location",
                "fieldtype": "Link",
                "options": "Location",
                "insert_after": "no_of_days_off"
            },
            {
                "fieldname": "job_title",
                "fieldtype": "Data",
                "label": "Job Title",
                "insert_after": "job_description_template",
                "reqd": 1
            }
        ]
    }
def get_job_applicant_custom_fields():
    '''
    Custom fields that need to be added to the Job Applicant Doctype
    '''
    return {
        "Job Applicant": [
            {
               "fieldname": "min_education_qual",
                "fieldtype": "Link",
                "label": "Educational Qualification",
                'options':"Educational Qualification",
                "insert_after": "details"
            },

            {
                "fieldname": "details",
                "fieldtype": "Section Break",
                "label": "Qualification Details",
                "insert_after": "applicant_rating"
            },

            {
                "fieldname": "min_experience",
                "fieldtype": "Float",
                "label": "Work Experience(in years)",
                "insert_after": "details_column_break"
            },
            {
                "fieldname": "details_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "min_education_qual"
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
                "reqd":1,
                "label": "Language Proficiency",
                "insert_after": "min_experience"
            },
            {
                "fieldname": "skill_proficiency",
                "fieldtype": "Table",
                "options": "Skill Proficiency",
                "label": "Skill Proficiency",
                "reqd":1,
                "insert_after": "language_proficiency"
            },
            {
                "fieldname": "location",
                "label": "Location",
                "fieldtype": "Link",
                "options": "Location",
                "insert_after": "country"
            },
            {
                "fieldname": "interview_process_break",
                "fieldtype": "Section Break",
                "label": "Interview Process",
                "insert_after": "skill_proficiency"
            },
            {
                "fieldname": "applicant_interview_round",
                "fieldtype": "Table",
                "options": "Applicant Interview Round",
                "label": "Interview Rounds",
                "insert_after": "interview_process_break"
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
                "fieldtype": "Table MultiSelect",
                "label": "Minimum Educational Qualification",
                'options':"Educational Qualifications",
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
            },
            {
                "fieldname": "location",
                "label": "Location",
                "fieldtype": "Link",
                "options": "Location",
                "insert_after": "no_of_days_off"
            },
             {
                 "fieldname": "skill_proficiency_break",
                 "fieldtype": "Section Break",
                 "label": "",
                 "insert_after": "job_details"
             },
             {
                "fieldname": "skill_proficiency",
                "fieldtype": "Table",
                "options": "Skill Proficiency",
                "label": "Skill Proficiency",
                "insert_after": "skill_proficiency_break"
            },
            {
                "fieldname": "skill_proficiency_description",
                "fieldtype": "HTML",
                "label": "",
                "options": "<p style='margin-top: 5px; color: #6c757d; font-size: 0.9em;'>Proficiency selected here is the minimum proficiency needed.</p>",
                "insert_after": "skill_proficiency"
            },
            {
                "fieldname": "job_requisition_id_",
                "label": "job Requisition",
                "fieldtype": "Link",
                "options": "Job Requisition",
                "insert_after": "designation"
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
            "doc_type": "Job Requisition",
            "field_name": "status",
            "property": "read_only",
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
            "doc_type": "Customer",
            "field_name": "sales_team_tab",
            "property": "hidden",
            "property_type": "TabBreak",
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
            "doc_type": "Item",
            "field_name": "grant_commission",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Customer",
            "field_name": "dn_required",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Item",
            "field_name": "include_item_in_manufacturing",
            "property": "default",
            "property_type": "Check",
            "value": 0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Item",
            "field_name": "inspection_required_before_delivery",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Item",
            "field_name": "manufacturing",
            "property": "depends_on",
            "property_type": "TabBreak",
            "value": "eval:doc.is_stock_item == 0"
        },
        {
            "doctype_or_field": "DocType",
            "doc_type": "Item",
            "property": "quick_entry",
            "property_type": "Check",
            "value": 0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "posting_date",
            "property": "read_only",
            "value": 1
        },
        {
            "doctype_or_field": "DocType",
            "doc_type": "Job Requisition",
            "property": "field_order",
            "value": "[\"workflow_state\", \"naming_series\", \"request_for\", \"employee_left\", \"staffing_plan\", \"designation\", \"column_break_qkna\", \"department\", \"no_of_positions\", \"expected_compensation\", \"column_break_4\", \"company\", \"status\", \"section_break_7\", \"requested_by\", \"requested_by_name\", \"column_break_10\", \"requested_by_dept\", \"requested_by_designation\", \"work_details\", \"employment_type\", \"no_of_days_off\", \"location\", \"work_details_column_break\", \"travel_required\", \"driving_license_needed\", \"is_work_shift_needed\", \"license_type\", \"education\", \"min_education_qual\", \"education_column_break\", \"min_experience\", \"reset_column\", \"language_proficiency\", \"skill_proficiency\", \"timelines_tab\", \"posting_date\", \"completed_on\", \"column_break_15\", \"expected_by\", \"time_to_fill\", \"job_description_tab\", \"job_description_template\", \"job_title\", \"description\", \"reason_for_requesting\", \"connections_tab\"]"
        }

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
                "label": "Is Agency",
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

def create_translation_quotation():
    translation = frappe.get_doc({
        'doctype': 'Translation',
        'source_text': 'Quotation',
        'translated_text': 'Release Order',
        'language': 'en'
    })
    translation.insert(ignore_permissions=True)
    frappe.db.commit()

create_translation_quotation()

def create_translation_quotation_to():
    translation = frappe.get_doc({
        'doctype': 'Translation',
        'source_text': 'Quotation To',
        'translated_text': 'Release Order To',
        'language': 'en'
    })
    translation.insert(ignore_permissions=True)
    frappe.db.commit()

create_translation_quotation_to()



def get_interview_feedback_custom_fields():
    '''
    Custom fields that need to be added to the Interview Feedback
    '''
    return {
        "Interview Feedback": [
            {
                "fieldname": "interview_question_result",
                "label": "Interview Question Result",
                "fieldtype": "Table",
                "options": "Interview Question Result",
                "insert_after": "skill_assessment"
            }
        ]
    }

def get_skill_assessment_custom_fields():
    '''
    Custom fields that need to be added to the Skill Assessment Child Table
    '''
    return {
        "Skill Assessment": [
            {
                "fieldname": "score",
                "fieldtype": "Float",
                "label": "Score",
                "reqd": 1,
                "insert_after":"skill"
            },
            {
                "fieldname": "remarks",
                "fieldtype": "Small Text",
                "label": "Remarks",
                "insert_after":"score"
            },
            {
                "fieldname": "weight",
                "fieldtype": "Float",
                "label": "weight",
                "insert_after":"remarks"
            }
        ]
    }
