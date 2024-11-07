import os
import click
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    #Creating BEAMS specific custom fields
    create_custom_fields(get_customer_custom_fields(), ignore_validate=True)
    create_custom_fields(get_sales_invoice_custom_fields(), ignore_validate=True)
    create_custom_fields(get_quotation_custom_fields(), ignore_validate=True)
    create_custom_fields(get_purchase_invoice_custom_fields(), ignore_validate=True)
    create_custom_fields(get_supplier_custom_fields(), ignore_validate=True)
    create_custom_fields(get_item_custom_fields(), ignore_validate=True)
    create_custom_fields(get_driver_custom_fields(), ignore_validate=True)
    create_custom_fields(get_employee_custom_fields(), ignore_validate=True)
    create_custom_fields(get_purchase_order_custom_fields(),ignore_validate=True)
    create_custom_fields(get_material_request_custom_fields(), ignore_validate=True)
    create_custom_fields(get_sales_order_custom_fields(), ignore_validate=True)
    create_custom_fields(get_employee_advance_custom_fields(), ignore_validate=True)
    create_custom_fields(get_journal_entry_custom_fields(), ignore_validate=True)
    create_custom_fields(get_voucher_entry_custom_fields(), ignore_validate=True)
    create_custom_fields(get_contract_custom_fields(),ignore_validate=True)
    create_custom_fields(get_department_custom_fields(),ignore_validate=True)
    create_custom_fields(get_job_requisition_custom_fields(),ignore_validate=True)
    create_custom_fields(get_job_opening_custom_fields(),ignore_validate=True)
    create_custom_fields(get_expected_skill_set_custom_fields(),ignore_validate=True)
    create_custom_fields(get_interview_round_custom_fields(),ignore_validate=True)
    create_custom_fields(get_job_applicant_custom_fields(),ignore_validate=True)
    create_custom_fields(get_budget_custom_fields(),ignore_validate=True)
    create_custom_fields(get_interview_feedback_custom_fields(),ignore_validate=True)
    create_custom_fields(get_skill_assessment_custom_fields(), ignore_validate=True)
    create_custom_fields(get_job_offer_custom_fields(), ignore_validate=True)


    #Creating BEAMS specific Property Setters
    create_property_setters(get_property_setters())

    #Creating BEAMS specific Roles
    create_custom_roles(get_beams_roles())

    #Creating BEAMS specific Translations
    create_translations(get_custom_translations())

    #Creating BEAMS specific Email Template
    create_email_templates(get_email_templates())

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
    delete_custom_fields(get_job_opening_custom_fields())
    delete_custom_fields(get_job_applicant_custom_fields())
    delete_custom_fields(get_budget_custom_fields())
    delete_custom_fields(get_expected_skill_set_custom_fields())
    delete_custom_fields(get_interview_round_custom_fields())
    delete_custom_fields(get_skill_assessment_custom_fields())
    delete_custom_fields(get_job_offer_custom_fields())

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
                "fieldname": "region",
                "fieldtype": "Link",
                "label": "Region",
                "options": "Region",
                "insert_after": "msme_status"
            },
            {
                "fieldname": "is_agent",
                "fieldtype": "Check",
                "label": "Is Agency",
                "insert_after": "region"
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
            },
        ]
    }

def get_job_offer_custom_fields():
    '''
    Custom fields that need to be added to the Job Offer DocType
    '''
    return {
        "Job Offer": [
            {
                "fieldname": "job_proposal",
                "fieldtype": "Link",
                "label": "Job Proposal",
                "options":"Job Proposal",
                "insert_after": "job_applicant",
                "read_only":1
            },
            {
                "fieldname": "ctc",
                "fieldtype": "Currency",
                "label": "CTC",
                "insert_after": "job_proposal",
                "fetch_from" : "job_proposal.proposed_ctc"
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
        ],
        "Budget Account": [
            {
                "fieldname": "cost_subhead",
                "fieldtype": "Link",
                "label": "Cost Sub Head",
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
                "insert_after": "amended_from"
            },
            {
                "fieldname": "sales_type",
                "fieldtype": "Link",
                "label": "Default Sales Type",
                "insert_after": "customer_purchase_order_reference",
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
                "insert_after": "customer_name",
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
                "insert_after": "albatross_details_section",
                "read_only":1
            },
            {
                "fieldname": "albatross_invoice_number",
                "fieldtype": "Data",
                "label": "Albatross Invoice Number",
                "insert_after": "albatross_ro_id",
                "read_only":1
            },
            {
                "fieldname": "albatross_ref_number",
                "fieldtype": "Data",
                "label": "Albatross Ref Number",
                "insert_after": "albatross_invoice_number",
                "read_only":1
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
                "insert_after": "albatross_column_break",
                "read_only":1
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
                "fetch_from": "party_name.is_agent",
                "depends_on": "eval:doc.is_agent",
                "insert_after": "party_name"
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
                "fieldname": "executive_name",
                "fieldtype": "Data",
                "label": "Executive Name",
                "insert_after": "client_name",
                "read_only":1
            }

        ],
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
               "fieldname": "date_of_birth",
                "fieldtype": "Date",
                "label": "Date of Birth",
                "insert_after": "email_id"
            },
            {
               "fieldname": "gender",
                "fieldtype": "Link",
                "label": "Gender",
                "options": "Gender",
                "insert_after": "date_of_birth"
            },
            {
                "fieldname": "willing_to_work_on_location",
                "fieldtype": "Check",
                "label": "Willing to work on the selected location?",
                "insert_after": "country"
            },
            {
               "fieldname": "father_name",
                "fieldtype": "Data",
                "label": "Father's Name",
                "insert_after": "job_title"
            },
            {
               "fieldname": "marital_status",
                "fieldtype": "Select",
                "label": "Marital Status",
                "options": "\nSingle\nMarried\nDivorced\nWidowed",
                "insert_after": "location"
            },
            {
                "fieldname": "current_address_session_break",
                "fieldtype": "Section Break",
                "label": "Current Address",
                "insert_after": "marital_status"
            },
            {
               "fieldname": "current_address",
                "fieldtype": "Small Text",
                "label": "Current Address",
                "insert_after": "current_address_session_break"
            },
            {
               "fieldname": "current_mobile_no",
                "fieldtype": "Data",
                "options": "Phone",
                "label": "Mobile Number",
                "insert_after": "current_address"
            },

            {
               "fieldname": "current_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "current_mobile_no"
            },
            {
               "fieldname": "current_period_from",
                "fieldtype": "Int",
                "label": "Period of From stay",
                "insert_after": "current_column_break"
            },
            {
               "fieldname": "current_period_to",
                "fieldtype": "Int",
                "label": "Period of To stay",
                "insert_after": "current_period_from"
            },
            {
               "fieldname": "current_residence_no",
                "fieldtype": "Int",
                "label": "Residence Number",
                "insert_after": "current_period_to"
            },
            {
                "fieldname": "permanent_address_session_break",
                "fieldtype": "Section Break",
                "label": "Permanent Address",
                "insert_after": "current_residence_no"
            },
            {
               "fieldname": "permanent_address",
                "fieldtype": "Small Text",
                "label": "Permanent Address",
                "insert_after": "permanent_address_session_break"
            },
            {
               "fieldname": "permanent_residence_no",
                "fieldtype": "Int",
                "label": "Residence Number",
                "insert_after": "permanent_address"
            },
            {
               "fieldname": "permanent_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "permanent_residence_no"
            },
            {
               "fieldname": "permanent_period_from",
                "fieldtype": "Int",
                "label": "Period of From stay",
                "insert_after": "permanent_column_break"
            },
            {
               "fieldname": "permanent_period_to",
                "fieldtype": "Int",
                "label": "Period of To stay",
                "insert_after": "permanent_period_from"
            },
            {
               "fieldname": "permananet_email_id",
                "fieldtype": "Data",
                "options": "Email",
                "label": "Email ID",
                "insert_after": "permanent_period_to"
            },
            {
                "fieldname": "email_address_session_break",
                "fieldtype": "Section Break",
                "label": "",
                "insert_after": "permananet_email_id"
            },
            {
               "fieldname": "email_id_1",
                "fieldtype": "Data",
                "options": "Email",
                "label": "Email ID",
                "insert_after": "email_address_session_break"
            },
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
                "fieldname": "department",
                "fieldtype": "Link",
                "label": "Department",
                "options": "Department",
                "insert_after": "designation"
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
                "fieldname": "education_qualification",
                "fieldtype": "Table",
                "options": "Education Qualification",
                "label": "Education Qualification",
                "insert_after": "applicant_interview_round"
            },
            {
                "fieldname": "professional_certification",
                "fieldtype": "Table",
                "options": "Professional Certification",
                "label": "Professional Certification",
                "insert_after": "education_qualification"
            },
            {
                "fieldname": "location",
                "label": "Location",
                "fieldtype": "Link",
                "options": "Location",
                "insert_after": "status"
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
            },
            {
                "fieldname": "current_employer_tab_break",
                "fieldtype": "Tab Break",
                "label": "Current Employer Details",
                "insert_after": "upper_range"
            },
            {
                "fieldname": "current_employer",
                "fieldtype": "Section Break",
                "label": "Current Employer / Immediate Previous Employer",
                "insert_after": "current_employer_tab_break"
            },
            {
                "fieldname": "name_of_employer",
                "fieldtype": "Data",
                "label": "Name of Employer",
                "insert_after": "current_employer"
            },
            {
                "fieldname": "employee_code",
                "fieldtype": "Data",
                "label": "Employee Code",
                "insert_after": "name_of_employer"
            },
            {
                "fieldname": "telephone_no",
                "fieldtype": "Data",
                "options": "Phone",
                "label": "Telephone No",
                "insert_after": "employee_code"
            },
            {
                "fieldname": "employment_period_from",
                "fieldtype": "Int",
                "label": "Employment Period From",
                "insert_after": "telephone_no"
            },
            {
                "fieldname": "employment_period_to",
                "fieldtype": "Int",
                "label": "Employment Period To",
                "insert_after": "employment_period_from"
            },
            {
                "fieldname": "address_of_employer",
                "fieldtype": "Small Text",
                "label": "Address of Employer",
                "insert_after": "employment_period_to"
            },

            {
                "fieldname": "current_employer_1_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "address_of_employer"
            },

            {
                "fieldname": "first_salary_drawn",
                "fieldtype": "Currency",
                "label": "First Salary Drawn",
                "insert_after": "current_employer_1_column_break"
            },
            {
                "fieldname": "last_salary_drawn",
                "fieldtype": "Currency",
                "label": "Last Salary Drawn",
                "insert_after": "first_salary_drawn"
            },
            {
                "fieldname": "current_designation",
                "fieldtype": "Data",
                "label": "Designation",
                "insert_after": "last_salary_drawn"
            },
            {
                "fieldname": "reference_taken",
                "fieldtype": "Select",
                "label": "Can a reference taken now?",
                "options": "\nYes\nNo",
                "insert_after": "current_designation"
            },
            {
                "fieldname": "was_this_position",
                "fieldtype": "Select",
                "label": "Was this Position Permanent,Temporary,Contractual?",
                "options": "\nPermanent\nTemporary\nContractual",
                "insert_after": "reference_taken"
            },
            {
                "fieldname": "duties_and_reponsibilities",
                "fieldtype": "Small Text",
                "label": "Duties and Responsibilities",
                "insert_after": "was_this_position"
            },
            {
                "fieldname": "current_employer_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "was_this_position"
            },
            {
                "fieldname": "current_department",
                "fieldtype": "Data",
                "label": "Department",
                "insert_after": "current_employer_column_break"
            },
            {
                "fieldname": "manager_name",
                "fieldtype": "Data",
                "label": "Manager's Name",
                "insert_after": "current_department"
            },
            {
                "fieldname": "manager_contact_no",
                "fieldtype": "Data",
                "options": "Phone",
                "label": "Manager's Contact No",
                "insert_after": "manager_name"
            },
            {
                "fieldname": "manager_email",
                "fieldtype": "Data",
                "options": "Email",
                "label": "Manager's Email",
                "insert_after": "manager_contact_no"
            },
            {
                "fieldname": "reason_for_leaving",
                "fieldtype": "Small Text",
                "label": "Reason For Leaving",
                "insert_after": "manager_email"
            },
            {
                "fieldname": "agency_details",
                "fieldtype": "Small Text",
                "label": "Agency Details(if temporary or contractual)",
                "insert_after": "reason_for_leaving"
            },
            {
                "fieldname": "previous_emplyoment",
                "fieldtype": "Section Break",
                "label": "Previous Employment History",
                "insert_after": "agency_details"
            },
            {
                "fieldname": "prev_emp_his",
                "fieldtype": "Table",
                "options": "Previous Employment History",
                "insert_after": "previous_emplyoment"
            },
            {
                "fieldname": "more_details_tab_break",
                "fieldtype": "Tab Break",
                "label": "More Details",
                "insert_after": "prev_emp_his"
            },
            {
                "fieldname": "current_salary",
                "fieldtype": "Currency",
                "label": "Current Salary",
                "insert_after": "more_details_tab_break"
            },
            {
                "fieldname": "current_salary_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "current_salary"
            },
            {
                "fieldname": "expected_salary",
                "fieldtype": "Currency",
                "label": "Expected Salary",
                "insert_after": "current_salary_column_break"
            },
            {
                "fieldname": "expected_salary_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "expected_salary"
            },
            {
                "fieldname": "telephone_number",
                "fieldtype": "Data",
                "options": "Phone",
                "label": "Telephone Number",
                "insert_after": "expected_salary_column_break"
            },
            {
                "fieldname": "other_achievments_session_break",
                "fieldtype": "Section Break",
                "label": "",
                "insert_after": "current_employer_tab_break"
            },
            {
                "fieldname": "other_achievments",
                "fieldtype": "Small Text",
                "label": "Please add details of Professional and other achievements,awards and accomplishments,if any",
                "insert_after": "other_achievments_session_break"
            },
            {
                "fieldname": "interviewed_session_break",
                "fieldtype": "Section Break",
                "label": "Have you been interviewed before by Madhyamam Group?If yes, Please give details below :",
                "insert_after": "other_achievments"
            },
            {
                "fieldname": "position",
                "fieldtype": "Data",
                "label": "Position",
                "insert_after": "interviewed_session_break"
            },
            {
                "fieldname": "interviewed_date",
                "fieldtype": "Date",
                "label": "Date",
                "insert_after": "position"
            },
            {
                "fieldname": "interviewed_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "interviewed_date"
            },
            {
                "fieldname": "interviewed_location",
                "fieldtype": "Link",
                "options": "Location",
                "label": "Location",
                "insert_after": "interviewed_column_break"
            },
            {
                "fieldname": "interviewed_outcome",
                "fieldtype": "Data",
                "label": "Outcome",
                "insert_after": "interviewed_location"
            },
            {
                "fieldname": "travel_session_break",
                "fieldtype": "Section Break",
                "label": "Are you willing to travel :",
                "insert_after": "interviewed_outcome"
            },
            {
                "fieldname": "in_india",
                "fieldtype": "Check",
                "label": "In India",
                "insert_after": "travel_session_break"
            },
            {
                "fieldname": "state_restriction",
                "fieldtype": "Data",
                "label": "State Restriction If any",
                "depends_on": "eval:doc.in_india",
                "insert_after": "in_india"
            },
            {
                "fieldname": "india_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "state_restriction"
            },
            {
                "fieldname": "abroad",
                "fieldtype": "Check",
                "label": "Abroad",
                "insert_after": "india_column_break"
            },
            {
                "fieldname": "related_session_break",
                "fieldtype": "Section Break",
                "label": "Are you related to any of employee of the Madhyamam Group? If yes,please give details :",
                "insert_after": "state_restriction"
            },
            {
                "fieldname": "related_employee",
                "fieldtype": "Data",
                "label": "Name",
                "insert_after": "related_session_break"
            },
            {
                "fieldname": "related_employee_org",
                "fieldtype": "Data",
                "label": "Organization",
                "insert_after": "related_employee"
            },
            {
                "fieldname": "related_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "related_employee_org"
            },
            {
                "fieldname": "related_employee_pos",
                "fieldtype": "Data",
                "label": "Position",
                "insert_after": "related_column_break",
            },
            {
                "fieldname": "related_employee_rel",
                "fieldtype": "Data",
                "label": "Relationship",
                "insert_after": "related_employee_pos"
            },
            {
                "fieldname": "prof_session_break",
                "fieldtype": "Section Break",
                "label": "",
                "insert_after": "related_employee_rel"
            },
            {
                "fieldname": "professional_org",
                "fieldtype": "Small Text",
                "label": "Are you a member of any Professional Organization? If yes, Please give details :",
                "insert_after": "prof_session_break"
            },
            {
                "fieldname": "political_org",
                "fieldtype": "Small Text",
                "label": "Are you a member of any Political Organization? If yes, Please give details :",
                "insert_after": "professional_org"
            },
            {
                "fieldname": "specialised_training",
                "fieldtype": "Small Text",
                "label": "Have you attended any specialised training program?If yes, Please give detais :",
                "insert_after": "political_org"
            },
            {
                "fieldname": "is_form_submitted",
                "fieldtype": "Check",
                "label": "Is Form Submitted",
                "read_only":1,
                "insert_after": "specialised_training"
            },
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
            "doctype_or_field": "DocField",
            "doc_type": "Job Applicant",
            "field_name": "status",
            "property": "options",
            "value": "Open\nReplied\nRejected\nLocal Enquiry Approved\nSelected\nHold\nAccepted\nTraining Completed\nLocal Enquiry Started\nLocal Enquiry Completed\nLocal Enquiry Rejected"
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
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "status",
            "property": "options",
            "value": "Pending\nOpen & Approved\nRejected\nFilled\nOn Hold\nCancelled"
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

def create_custom_roles(roles):
    '''
        Method to create custom Role
        args:
            roles : Role List (list of string)
        example:
            ["HOD", "Manager"]
    '''
    for role in roles:
        if not frappe.db.exists("Role", role):
            role_doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": role
            })
            role_doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_translations(translations):
    for translation in translations:
        if not frappe.db.exists(translation):
            frappe.get_doc(translation).insert(ignore_permissions=True)
    frappe.db.commit()

def create_email_templates(email_templates):
    '''
        Method to Create Email Template
        args:
            email_templates : Email Template List
    '''
    for email_template in email_templates:
        if not frappe.db.exists('Email Template', email_template.get('name')):
            frappe.get_doc(email_template).insert(ignore_permissions=True)
    frappe.db.commit()

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

def get_beams_roles():
    '''
        Method to get BEAMS specific roles
    '''
    return ['Production Manager', 'CEO', 'Company Secretary', 'HOD','Enquiry Officer','Enquiry Manager']

def get_custom_translations():
    '''
        Method to get Translations
    '''
    return [
        {
            'doctype': 'Translation',
            'source_text': 'Quotation To',
            'translated_text': 'Release Order To',
            'language': 'en'
        },
        {
            'doctype': 'Translation',
            'source_text': 'Quotation',
            'translated_text': 'Release Order',
            'language': 'en'
        }
    ]

def get_email_templates():
    '''
        Method to get Email Templates
    '''
    return [
        {
            'doctype': 'Email Template',
            'name': 'Job Applicant Follow Up',
            'subject': "{{applicant_name}}, Complete your Application",
            'response': """Dear {{ applicant_name }},
                           We're excited to move forward with your application!
                           To continue, please upload the required documents by clicking the link: <a href="{{ magic_link }}">Click Here</a>.
                           Thank you for your interest in joining us!
                           If you have any questions, feel free to reach out.
                           Best regards,
                           HR Manager"""
        }
]
