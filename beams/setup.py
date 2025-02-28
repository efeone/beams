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
    create_custom_fields(get_company_custom_fields(), ignore_validate=True)
    create_custom_fields(get_training_event_employee_custom_fields(), ignore_validate=True)
    create_custom_fields(get_attendance_request_custom_fields(),ignore_validate=True)
    create_custom_fields(get_shift_assignment_custom_fields(),ignore_validate=True)
    create_custom_fields(get_leave_type_custom_fields(),ignore_validate=True)
    create_custom_fields(get_leave_application_custom_fields(),ignore_validate=True)
    create_custom_fields(get_employee_performance_feedback(),ignore_validate=True)
    create_custom_fields(get_employment_type(),ignore_validate=True)
    create_custom_fields(get_appointment_letter(),ignore_validate=True)
    create_custom_fields(get_employment_type_custom_fields(),ignore_validate=True)
    create_custom_fields(get_employee_separation_custom_fields(),ignore_validate=True)
    create_custom_fields(get_appraisal_template_custom_fields(),ignore_validate=True)
    create_custom_fields(get_employee_feedback_rating_custom_fields(),ignore_validate=True)
    create_custom_fields(get_appraisal_custom_fields(),ignore_validate=True)
    create_custom_fields(get_appraisal_kra_custom_fields(),ignore_validate=True)
    create_custom_fields(get_event_custom_fields(),ignore_validate=True)
    create_custom_fields(get_project_custom_fields(),ignore_validate=True)
    create_custom_fields(get_Payroll_Settings_custom_fields(),ignore_validate=True)
    create_custom_fields(get_asset_custom_fields(),ignore_validate=True)
    create_custom_fields(get_vehicle_custom_fields(),ignore_validate=True)
    create_custom_fields(get_interview_custom_fields(),ignore_validate=True)
    create_custom_fields(get_item_group_custom_fields(),ignore_validate=True)
    create_custom_fields(get_hr_settings_custom_fields(),ignore_validate=True)
    create_custom_fields(get_asset_category_custom_fields(),ignore_validate=True)


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
    delete_custom_fields(get_company_custom_fields())
    delete_custom_fields(get_training_event_employee_custom_fields())
    delete_custom_fields(get_attendance_request_custom_fields())
    delete_custom_fields(get_shift_assignment_custom_fields())
    delete_custom_fields(get_leave_type_custom_fields())
    delete_custom_fields(get_leave_application_custom_fields())
    delete_custom_fields(get_employee_performance_feedback())
    delete_custom_fields(get_employment_type())
    delete_custom_fields(get_appointment_letter())
    delete_custom_fields(get_employment_type_custom_fields())
    delete_custom_fields(get_employee_separation_custom_fields())
    delete_custom_fields(get_appraisal_template_custom_fields())
    delete_custom_fields(get_employee_feedback_rating_custom_fields())
    delete_custom_fields(get_appraisal_custom_fields())
    delete_custom_fields(get_appraisal_kra_custom_fields())
    delete_custom_fields(get_event_custom_fields())
    delete_custom_fields(get_project_custom_fields())
    delete_custom_fields(get_Payroll_Settings_custom_fields())
    delete_custom_fields(get_asset_custom_fields())
    delete_custom_fields(get_vehicle_custom_fields())
    delete_custom_fields(get_interview_custom_fields())
    delete_custom_fields(get_item_group_custom_fields())
    delete_custom_fields(get_hr_settings_custom_fields())
    delete_custom_fields(get_asset_category_custom_fields())


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

def get_shift_assignment_custom_fields():
    '''
    Custom fields that need to be added to the Shift Assignment DocType
    '''
    return {
        "Shift Assignment": [
            {
                "fieldname": "roster_type",
                "fieldtype": "Select",
                "label": "Roster Type",
                "options":"\nRegular\nDouble Shift",
                "insert_after": "shift_type"
            }
        ]
    }

def get_Payroll_Settings_custom_fields():
    '''
    Custom fields that need to be added to the Payroll Settings Doctype
    '''
    return {
        "Payroll Settings": [
            {
                "fieldname": "provident_fund_section",
                "fieldtype": "Section Break",
                "label": "Provident Fund",
                "insert_after": "show_leave_balances_in_salary_slip"
            },
            {
                "fieldname": "employer_pf_contribution",
                "label": "Employer PF Contribution",
                "fieldtype": "Percent",
                "insert_after": "provident_fund_section"
            },
            {
                "fieldname": "column_break_pf",
                "fieldtype": "Column Break",
                "insert_after": "employer_pf_contribution"
            },
            {
                "fieldname": "pf_expense_account",
                "label": "PF Expense Account",
                "fieldtype": "Link",
                "options": "Account",
                "insert_after": "column_break_pf"
            },
            {
                "fieldname": "esi_section",
                "fieldtype": "Section Break",
                "label": "Employees State Insurance",
                "insert_after": "pf_expense_account"
            },
            {
                "fieldname": "esi_employer_contribution",
                "label": "ESI Employer Contribution",
                "fieldtype": "Percent",
                "insert_after": "esi_section"
            },
            {
                "fieldname": "column_break_esi",
                "fieldtype": "Column Break",
                "insert_after": "esi_employer_contribution"
            },
            {
                "fieldname": "esi_expense_account",
                "label": "ESI Expense Account",
                "fieldtype": "Link",
                "options": "Account",
                "insert_after": "column_break_esi"
            }
        ]
    }

def get_project_custom_fields():
    '''
    Custom fields that need to be added to the Project Doctype
    '''
    return {
        "Project": [
            {
                "fieldname": "program_section",
                "fieldtype": "Section Break",
                "label": "Program Details",
                "collapsible": 1,
                "insert_after": "sales_order"
            },
            {
                "fieldname": "program_request",
                "label": "Program Request",
                "fieldtype": "Link",
                "options": "Program Request",
                "insert_after": "program_section"
            },
            {
                "fieldname": "bureau",
                "label": "Bureau",
                "fieldtype": "Link",
                "options":"Bureau",
                "insert_after": "expected_revenue",
                "fetch_from": "program_request.bureau",
                "read_only": 1

            },
            {
                "fieldname": "column_break_program",
                "fieldtype": "Column Break",
                "insert_after": "generates_revenue"
            },
            {
                "fieldname": "program_type",
                "label": "Program Type",
                "fieldtype": "Link",
                "options": "Program Type",
                "insert_after": "column_break_program",
                "fetch_from": "program_request.program_type",
                "read_only": 1
            },
            {
                "fieldname": "budget_expense_types",
                "fieldtype": "Table MultiSelect",
                "label": "Budget Expense Types",
                'options':"Project Expense Type",
                "insert_after": "program_type"
            },
            {
                "fieldname": "generates_revenue",
                "fieldtype": "Check",
                "label": "Generates Revenue",
                "read_only": 1,
                "fetch_from": "program_request.generates_revenue",
                "insert_after": "program_request"
            },
            {
                "fieldname": "expected_revenue",
                "fieldtype": "Float",
                "label": "Expected Revenue",
                "read_only": 1,
                "fetch_from": "program_request.expected_revenue",
                "insert_after": "generates_revenue"
            },
            {
                "fieldname": "allocated_resources_details_section",
                "fieldtype": "Section Break",
                "label": " Allocated Resource Details",
                "collapsible": 1,
                "insert_after": "program_request"
            },
            {
                "fieldname": "allocated_resources_details",
                "fieldtype": "Table",
                "label": "Allocated Resource Detail",
                "options":"Allocated Resource Detail",
                "insert_after":"allocated_resources_details_section"
            },
            {
                "fieldname": "approved_budget",
                "fieldtype": "Currency",
                "label": "Approved Budget",
                "options":"approved_budget",
                "insert_after":"budget_expense_types",
                "read_only": 1

            },
            {
                "fieldname": "estimated_budget",
                "fieldtype": "Currency",
                "label": "Estimated Budget",
                "options":"Estimated Budget",
                "fetch_from": "program_request.estimated_budget",
                "insert_after":"approved_budget",
                "read_only": 1
            },
            {
                "fieldname": "description",
                "fieldtype": "Small Text",
                "label": "Description",
                "fetch_from":"program_request.description",
                "insert_after": "bureau"
            },
            {
                "fieldname": "requirements",
                "fieldtype": "Text Editor",
                "label": "Requirements",
                "fetch_from":"program_request.requirements",
                "insert_after": "description"
            },
            {
                "fieldname": "location",
                "fieldtype": "Link",
                "label": "Location",
                "options":"Location",
                "fetch_from":"program_request.location",
                "insert_after": "department",
                "fetch_on_save_if_empty":1
            }

        ]
    }

def get_employment_type_custom_fields():
    '''
    Custom fields that need to be added to the Employment Type DocType
    '''
    return {
        "Employment Type": [
            {
                "fieldname": "penalty_leave_type",
                "fieldtype": "Link",
                "label": "Penalty Leave Type",
                "options": "Leave Type",
                "insert_after": "employee_type_name"
            }
        ]
    }

def get_event_custom_fields():
    '''
    Custom fields to be added to the Event Doctype
    '''
    return {
        "Event": [
            {
                "fieldname": "contribution_of_employee",
                "fieldtype": "Small Text",
                "label": "Contribution of Employee",
                "insert_after": "description",
                "depends_on": "eval:doc.event_category == 'One to One Meeting'"
            },
            {
                "fieldname": "improvement_of_employee",
                "fieldtype": "Small Text",
                "label": "Areas of Improvement of Employee",
                "insert_after": "contribution_of_employee",
                "depends_on": "eval:doc.event_category == 'One to One Meeting'"
            },
            {
                "fieldname": "training_needs_of_employee",
                "fieldtype": "Small Text",
                "label": "Training Needs of Employee",
                "insert_after": "improvement_of_employee",
                "depends_on": "eval:doc.event_category == 'One to One Meeting'"
            },
            {
                "fieldname": "is_employee_eligible_for_promotion",
                "fieldtype": "Select",
                "label": "Is Employee Eligible for Promotion",
                "options": "\nYes\nNo",
                "insert_after": "training_needs_of_employee",
                "depends_on": "eval:doc.event_category == 'One to One Meeting'"
            },
            {
                "fieldname": "remarks_for_promotion",
                "fieldtype": "Small Text",
                "label": "Remarks",
                "insert_after": "is_employee_eligible_for_promotion",
                "depends_on": "eval:(doc.is_employee_eligible_for_promotion == 'Yes' || doc.is_employee_eligible_for_promotion == 'No') && doc.event_category == 'One to One Meeting'"
            },
            {
                "fieldname": "appraisal_reference",
                "fieldtype": "Link",
                "label": "Appraisal Reference",
                "options": "Appraisal",
                "insert_after": "status"
            },
            {
                "fieldname": "assign_service_unit",
                "fieldtype": "Check",
                "label": "Assign Service Unit",
                "insert_after": "add_video_conferencing"
            },
            {
                "fieldname": "meeting_room",
                "fieldtype": "Link",
                "label": "Meeting Room",
                "options": "Service Unit",
                "depends_on": "eval:doc.assign_service_unit == 1",
                "mandatory_depends_on": "eval:doc.assign_service_unit == 1",
                "insert_after": "assign_service_unit"
            },
            {
                "fieldname": "section_break_epd",
                "fieldtype": "Section Break",
                "label": " ",
                "insert_after": "sunday"
            },
            {
                "fieldname": "external_participants",
                "fieldtype": "Table",
                "label": "External Participants",
                "options": "External Participants Detail",
                "insert_after": "section_break_epd"
            },
            {
                "fieldname": "reason_for_rejection",
                "fieldtype": "Small Text",
                "label": "Reason for Rejection",
                "insert_after": "repeat_this_event"
            }
        ]
    }

def get_leave_application_custom_fields():
    '''
    Custom fields that need to be added to the Leave Application  Doctype
    '''
    return {
        "Leave Application": [
            {
                "fieldname": "medical_certificate",
                "fieldtype": "Attach",
                "label": "Medical Certificate",
                "hidden": 1,
               "insert_after": "leave_type"
            }

        ]
    }
def get_attendance_request_custom_fields():
    """
    Custom fields that need to be added to the Attendance Request DocType.
    """
    return {
        "Attendance Request": [
            {
                "fieldname": "reports_to",
                "fieldtype": "Link",
                "label": "Reports To",
                "options": "Employee",
                "fetch_from":"employee.reports_to",
                "insert_after": "reason"
            },
            {
                "fieldname": "reports_to_name",
                "fieldtype": "Data",
                "label": "Reports To Name",
                "insert_after": "reports_to",
                "fetch_from": "reports_to.employee_name"
            },
            {
                "fieldname": "reports_to_user",
                "fieldtype": "Link",
                "label": "Reports To User",
                "options": "User",
                "insert_after": "reports_to_name",
                "fetch_from": "reports_to.user_id"
            }
        ]
    }

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
                "mandatory_depends_on": "eval:doc.is_agent",
                "insert_after": "msme_status"
            },
            {
                "fieldname": "is_agent",
                "fieldtype": "Check",
                "label": "Is Agency",
                "insert_after": "region"
            },
            {
                "fieldname": "is_edited",
                "fieldtype": "Check",
                "label": "Is Edited",
                "hidden": 1,
                "default": 0,
                "no_copy":1,
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
                "fieldname": "head_of_department_name",
                "fieldtype": "Data",
                "label": "Head Of Department(Name)",
                "insert_after": "head_of_department",
                "fetch_from": "head_of_department.employee_name",
                "read_only": 1
            },
            {
                "fieldname": "abbreviation",
                "fieldtype": "Data",
                "label": "Abbreviation",
                "reqd":1,
                "unique":1,
                "insert_after": "head_of_department_name"
            },
            {
                "fieldname": "threshold_amount",
                "fieldtype": "Float",
                "label": "Threshold Amount",
                "insert_after": "parent_department"
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

def get_asset_custom_fields():
    '''
    Custom fields that need to be added to the Asset DocType
    '''
    return {
        "Asset": [
            {
                "fieldname": "bureau",
                "fieldtype": "Link",
                "options":"Bureau",
                "label": "Bureau",
                "insert_after": "location"
            },
            {
                "fieldname": "in_transit",
                "fieldtype": "Check",
                "label": "In Transit",
                "insert_after": "is_composite_asset",
                "allow_on_submit": 1,
                "read_only":1

            },
            {
                "fieldname": "warranty_details_section",
                "fieldtype": "Section Break",
                "label": "Warranty Details Section",
                "insert_after": "comprehensive_insurance",
                "collapsible": 1
            },
            {
                "fieldname": "warranty_reference_no",
                "fieldtype": "Data",
                "label": "Warranty Reference No",
                "insert_after": "warranty_details_section"
            },
            {
                "fieldname": "warranty_till",
                "fieldtype": "Date",
                "label": "Warranty Till",
                "insert_after": "warranty_reference_no"
            },
            {
                "fieldname": "qr_code",
                "fieldtype": "Attach Image",
                "label": "QR code",
                "insert_after": "department"
            }
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
                "insert_after": "applicant_email",
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
        ],
        "Purchase Order Item": [
            {
                "fieldname": "reference_doctype",
                "fieldtype": "Link",
                "label": "Reference DocType",
                "options":"DocType",
                "insert_after": "blanket_order_rate"
            },
            {

                "fieldname": "reference_document",
                "fieldtype": "Dynamic Link",
                "label": "Reference Document",
                "options":"reference_doctype",
                "insert_after": "reference_doctype"
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
                "reqd": 1,
                "insert_after": "company"
            },
            {
                "fieldname": "division",
                "fieldtype": "Link",
                "label": "Division",
                "options":"Division",
                "reqd": 1,
                "insert_after": "department"
            },
            {
                "fieldname": "region",
                "fieldtype": "Link",
                "label": "Region",
                "options":"Region",
                "insert_after": "budget_template"
            },
            {
                "fieldname": "budget_template",
                "fieldtype": "Link",
                "label": "Budget Template",
                "options":"Budget Template",
                "insert_after": "monthly_distribution"
            },
            {
                "fieldname": "rejection_feedback",
                "fieldtype": "Table",
                "label": "Rejection Feedback",
                "options":"Rejection Feedback",
                "insert_after": "december",
                "depends_on": "eval: doc.workflow_state.includes('Rejected')"
            }
        ],
        "Budget Account": [
            {
                "fieldname": "cost_head",
                "fieldtype": "Link",
                "label": "Cost Head",
                "options":"Cost Head",
                "insert_before": "cost_subhead",
                "in_list_view":1
            },
            {
                "fieldname": "cost_subhead",
                "fieldtype": "Link",
                "label": "Cost Sub Head",
                "options":"Cost Subhead",
                "insert_after": "cost_head",
                "in_list_view":1
            },
            {
                "fieldname": "cost_category",
                "fieldtype": "Link",
                "label": "Cost Category",
                "options":"Cost Category",
                "insert_after": "account",
                "in_list_view":1
            },
            {
                "fieldname": "column_break_cd",
                "fieldtype": "Column Break",
                "label": " ",
                "insert_after": "cost_category"
            },
            {
                "fieldname": "cost_description",
                "fieldtype": "Small Text",
                "label": "Cost Description",
                "insert_after": "column_break_cd"
            },
            {
                "fieldname": "equal_monthly_distribution",
                "fieldtype": "Check",
                "label": "Equal Monthly Distribution ",
                "insert_after": "cost_description"
            },
            {
                "fieldname": "section_break_ab",
                "fieldtype": "Section Break",
                "label": "Monthly Amount Distribution",
                "insert_after": "budget_amount"
            },
            {
                "fieldname": "january",
                "fieldtype": "Currency",
                "label": "January",
                "insert_after": "section_break_ab"
            },
            {
                "fieldname": "february",
                "fieldtype": "Currency",
                "label": "February",
                "insert_after": "january"
            },
            {
                "fieldname": "march",
                "fieldtype": "Currency",
                "label": "March",
                "insert_after": "february"
            },
            {
                "fieldname": "april",
                "fieldtype": "Currency",
                "label": "April",
                "insert_after": "march"
            },
            {
                "fieldname": "column_break_bc",
                "fieldtype": "Column Break",
                "label": " ",
                "insert_after": "april"
            },
            {
                "fieldname": "may",
                "fieldtype": "Currency",
                "label": "May",
                "insert_after": "column_break_bc"
            },
            {
                "fieldname": "june",
                "fieldtype": "Currency",
                "label": "June",
                "insert_after": "may"
            },
            {
                "fieldname": "july",
                "fieldtype": "Currency",
                "label": "July",
                "insert_after": "june"
            },
            {
                "fieldname": "august",
                "fieldtype": "Currency",
                "label": "August",
                "insert_after": "july"
            },
            {
                "fieldname": "column_break_ab",
                "fieldtype": "Column Break",
                "label": " ",
                "insert_after": "august"
            },
            {
                "fieldname": "september",
                "fieldtype": "Currency",
                "label": "September",
                "insert_after": "column_break_ab"
            },
            {
                "fieldname": "october",
                "fieldtype": "Currency",
                "label": "October",
                "insert_after": "september"
            },
            {
                "fieldname": "november",
                "fieldtype": "Currency",
                "label": "November",
                "insert_after": "october"
            },
            {
                "fieldname": "december",
                "fieldtype": "Currency",
                "label": "December",
                "insert_after": "november"
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
                "fieldname": "region",
                "fieldtype": "Link",
                "options": "Region",
                "label": "Region",
                "insert_after": "is_reverse_charge"
            },
            {
                "fieldname": "executive",
                "fieldtype": "Link",
                "options": "Employee",
                "label": "Executive",
                "insert_after": "due_date"
            },
            {
                "fieldname": "executive_name",
                "fieldtype": "Data",
                "label": "Executive Name",
                "insert_after": "executive",
                "fetch_from": "executive.employee_name",
                "read_only": 1
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
                "fieldname": "is_agent",
                "fieldtype": "Check",
                "label": "Is Agency",
                "read_only":1,
                "fetch_from": "party_name.is_agent",
                "depends_on": "eval:doc.is_agent",
                "insert_after": "party_name"
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
                "fieldname": "actual_customer_group",
                "fieldtype": "Link",
                "label": "Actual Customer Group",
                "options": "Customer Group",
                "read_only": 1,
                "fetch_from": "actual_customer.customer_group",
                "insert_after": "actual_customer"
            },
            {
                "fieldname": "customer_purchase_order_reference",
                "fieldtype": "Data",
                "label": "Customer Purchase Order Reference",
                "insert_after": "valid_till"
            },
            {
                "fieldname": "executive",
                "fieldtype": "Link",
                "label": "Executive",
                "options":"Employee",
                "insert_after": "customer_purchase_order_reference"
            },
            {
                "fieldname": "executive_name",
                "fieldtype": "Data",
                "label": "Executive Name",
                "insert_after": "executive",
                "fetch_from": "executive.employee_name",
                "read_only":1
            },
            {
                "fieldname": "is_barter",
                "fieldtype": "Check",
                "label": "Is Barter",
                "insert_after": "amended_from"
            },
            {
                "fieldname": "purchase_order",
                "fieldtype": "Link",
                "label": "Purchase Order",
                "insert_after": "is_barter",
                "depends_on": "eval:doc.is_barter",
                "options": "Purchase Order"
            },
            {
                "fieldname": "sales_type",
                "fieldtype": "Link",
                "label": "Default Sales Type",
                "insert_after": "purchase_order",
                "options": "Sales Type"
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
                "fieldname": "ro_no",
                "fieldtype": "Data",
                "label": "RO No",
                "insert_after": "albatross_ro_id",
                "read_only":1
            },
            {
                "fieldname": "ro_date",
                "fieldtype": "Date",
                "label": "RO Date",
                "insert_after": "ro_no",
                "read_only":1
            },
            {
                "fieldname": "ro_option",
                "fieldtype": "Data",
                "label": "RO Option",
                "insert_after": "ro_date",
                "read_only":1
            },
            {
                "fieldname": "region_revenue_percentage",
                "fieldtype": "Percent",
                "label": "Region Revenue Percentage",
                "insert_after": "ro_option",
                "read_only":1
            },
            {
                "fieldname": "albatross_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "region_revenue_percentage"
            },
            {
                "fieldname": "product_name",
                "fieldtype": "Data",
                "label": "Product Name",
                "insert_after": "albatross_column_break",
                "read_only":1
            },
            {
                "fieldname": "program_name",
                "fieldtype": "Data",
                "label": "Program Name",
                "insert_after": "product_name",
                "read_only":1
            },
            {
                "fieldname": "no_of_eps",
                "fieldtype": "Data",
                "label": "No of Episodes",
                "insert_after": "program_name",
                "read_only":1
            },
            {
                "fieldname": "commission_per",
                "fieldtype": "Float",
                "label": "Commission Per",
                "insert_after": "no_of_eps",
                "read_only":1
            },
            {
                "fieldname": "fct_total",
                "fieldtype": "Float",
                "label": "FCT Total",
                "insert_after": "commission_per",
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

def get_item_group_custom_fields():
    '''
    Custom fields that need to be added to the Quotation Item Doctype
    '''
    return {
        "Item Group": [
            {
                "fieldname": "hireable",
                "fieldtype": "Check",
                "label": "Hireable",
                "fetch_from":"parent_item_group.hireable",
                "set_only_once":1,
                "fetch_if_empty":1,
                "insert_after": "gst_hsn_code"
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
           },
           {
               "fieldname": "hireable",
               "fieldtype": "Check",
               "label": "Hireable",
               "fetch_from":"item_group.hireable",
               "set_only_once":1,
               "insert_after": "gst_hsn_code"
           },
           {
               "fieldname": "service_item",
               "fieldtype": "Link",
               "label": "Service Item",
               "options": "Item",
               "read_only":1,
               "insert_after": "item_group"
           },
           {
               "fieldname": "item_audit_notification",
               "fieldtype": "Check",
               "label": "Periodic Notification for Asset Auditing ",
               "depends_on": "eval:doc.is_fixed_asset == 1",
               "insert_after": "asset_category"
           },
           {
               "fieldname": "item_notification_frequency",
               "fieldtype": "Select",
               "label": "Notification Frequency",
               "options":"\nMonthly\nTrimonthly\nQuarterly\nHalf Yearly\nYearly",
               "depends_on": "eval:doc.item_audit_notification == 1",
               "insert_after": "item_audit_notification"
           }   ,
           {
               "fieldname": "item_notification_template",
               "fieldtype": "Link",
               "label": "Notification Template",
               "options":"Email Template",
               "depends_on": "eval:doc.item_audit_notification == 1",
               "insert_after": "item_notification_frequency"
           },
           {
               "fieldname": "start_notification_from",
               "fieldtype": "Select",
               "label": "Start Notification From",
               "options":"\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
               "depends_on": "eval:doc.item_audit_notification == 1",
               "insert_after": "item_audit_notification"
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
                "insert_after": "Bureau"
            },
            {
                "fieldname": "leave_policy",
                "fieldtype": "Link",
                "options": "Leave Policy",
                "label": "Leave Policy",
                "insert_after": "attendance_device_id"
            },
            {
                "fieldname": "name_of_father",
                "fieldtype": "Data",
                "label": "Father's Name",
                "insert_after": "date_of_birth"
            },
            {
                "fieldname": "name_of_spouse",
                "fieldtype": "Data",
                "label": "Spouse's Name",
                "insert_after": "name_of_father"
            },
            {
                "fieldname": "pincode",
                "fieldtype": "Data",
                "label": "Pincode",
                "insert_after": "address_section"
            },
            {
                "fieldname": "aadhar_id",
                "fieldtype": "Data",
                "label": "Aadhar Id",
                "insert_after": "marital_status"
            },
            {
                "fieldname": "date_of_appointment",
                "fieldtype": "Date",
                "label": "Date of Appointment",
                "insert_after": "date_of_joining"
            },
            {
                "fieldname": "nominee_details_section",
                "fieldtype": "Section Break",
                "label": "Nominee Details",
                "insert_after": "iban"
            },
            {
                "fieldname": "nominee_details",
                "fieldtype": "Table",
                "label": "Nominee Details",
                "options":"Nominee Details",
                "insert_after":"nominee_details_section"
            },
            {
                "fieldname": "additional_information_section",
                "fieldtype": "Section Break",
                "label": _("Additional Information"),
                "insert_after": "place_of_issue",
                "collapsible": 1
            },
            {
                "fieldname": "physical_disabilities",
                "fieldtype": "Select",
                "label": "Do you have a physical disability",
                "options":"Yes\nNo",
                "default": "No",
                "insert_after": "additional_information_section"
            },
            {
                "fieldname": "disabilities",
                "fieldtype": "Data",
                "label": "Please specify the disability",
                "insert_after": "physical_disabilities",
                "depends_on": "eval:doc.physical_disabilities == 'Yes'"
            },
            {
                "fieldname": "marital_indebtness",
                "fieldtype": "Select",
                "options":"Yes\nNo",
                "default": "No",
                "label": "Do you have marital indebtedness",
                "insert_after": "disabilities"
            },
            {
                "fieldname": "training_status",
                "fieldtype": "Select",
                "options":"Not Started\nIn Progress\nCompleted\nNot Completed\nPartially Completed",
                "label": "Training Status",
                "insert_after": "status"
            },
            {
                "fieldname": "court_proceedings",
                "fieldtype": "Select",
                "options":"Yes\nNo",
                "default": "No",
                "label": "Are there any ongoing court proceedings",
                "insert_after": "marital_indebtness",
            },
            {
                "fieldname": "court_proceedings_details",
                "fieldtype": "Small Text",
                "label": "Court Proceedings Details",
                "insert_after": "court_proceedings",
                "depends_on": "eval:doc.court_proceedings == 'Yes'"
            },
            {
                "fieldname": "column_break_travel",
                "fieldtype": "Column Break",
                "insert_after": "court_proceedings_details"
            },
            {
                "fieldname": "are_you_willing_to_travel",
                "label": "Are you willing to travel",
                "fieldtype": "Check",
                "insert_after": "column_break_travel",
            },
            {
                "fieldname": "in_india",
                "label": "In India",
                "fieldtype": "Select",
                "options":"Yes\nNo",
                "default":"No",
                "insert_after": "are_you_willing_to_travel",
                "depends_on": "eval:doc.are_you_willing_to_travel == 1"
            },
            {
                "fieldname": "abroad",
                "label": "Abroad",
                "fieldtype": "Select",
                "options":"Yes\nNo",
                "default":"No",
                "insert_after": "in_india",
                "depends_on": "eval:doc.are_you_willing_to_travel == 1"
            },
            {
                "fieldname": "state_restrictions_problems",
                "label": "State Restrictions/Problems if any",
                "fieldtype": "Data",
                "insert_after": "abroad",
                "depends_on": "eval:doc.are_you_willing_to_travel == 1"
            },
            {
                "fieldname": "places_to_travel",
                "label": "Places/Countries of your choice where you'd like to travel on job",
                "fieldtype": "Data",
                "insert_after": "state_restrictions_problems",
            },
            {
                "fieldname": "are_you_related_to_employee",
                "label": "Are you related to any of our employees",
                "fieldtype": "Check",
                "insert_after": "places_to_travel"
            },
            {
                "fieldname": "related_employee_name",
                "label": "Related Employee Name",
                "fieldtype": "Data",
                "insert_after": "are_you_related_to_employee",
                "depends_on": "eval:doc.are_you_related_to_employee == 1",
            },
            {
                "fieldname": "documents_tab",
                "fieldtype": "Tab Break",
                "label": "Documents",
                "insert_after": "internal_work_history"
            },
            {
                "fieldname": "employee_documents",
                "fieldtype": "Table",
                "label": "Employee Documents",
                "options":"Employee Documents",
                "insert_after":"documents_tab"
            },
            {
                "fieldname": "no_of_children",
                "fieldtype": "Data",
                "label": "No.of Children",
                "insert_after":"marital_status"
            },
        ],

        "Employee External Work History":[
            {
                "fieldname": "period_from",
                "fieldtype": "Date",
                "label": "Period From",
                "insert_after": "designation"
            },
            {
                "fieldname": "period_to",
                "fieldtype": "Date",
                "label": "Period To",
                "insert_after": "period_from"
            },
            {
                "fieldname": "last_position_held",
                "fieldtype": "Data",
                "label": "Last Position Held",
                "insert_after": "period_to"
            },
            {
                "fieldname": "job_responsibility",
                "fieldtype": "Small Text",
                "label": "Job Responsibility",
                "insert_after": "last_position_held"
            },
            {
                "fieldname": "designation_of_immediate_superior",
                "fieldtype": "Data",
                "label": "Designation Of Immediate Superior",
                "insert_after": "job_responsibility"
            },
            {
                "fieldname": "gross_salary_drawn",
                "fieldtype": "Float",
                "label": "Gross Salary Drawn ",
                "insert_after": "designation_of_immediate_superior"
            },
            {
                "fieldname": "reason_for_leaving",
                "fieldtype": "Small Text",
                "label": "Reason For Leaving",
                "insert_after": "gross_salary_drown"
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
                "fieldname": "expected_questions",
                "fieldtype": "Table",
                "label": "Interview Questions",
                "options":"Interview Questions",
                "insert_after":"expected_skill_set"
            }
        ]
    }

def get_interview_custom_fields():
    '''
    Custom fields that need to be added to the Interview Doctype
    '''
    return {
        "Interview": [
            {
                "fieldname": "department",
                "fieldtype": "Link",
                "options": "Department",
                "label": "Department",
                "insert_after": "job_applicant",
                "fetch_from": "job_applicant.department"
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
                "fieldname": "suggestions_details_section",
                "fieldtype": "Section Break",
                "label": "",
                "insert_after": "skill_proficiency"
            },
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
                "insert_after": "department",
                "permlevel": 1
            },

            {
                "fieldname": "no_of_days_off",
                "fieldtype": "Int",
                "label": "Number of Days Off",
                "description": " Number Of Days Off Within a 30-day Period",
                "insert_after": "work_details",
                "permlevel": 1
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
                "insert_after": "work_details_column_break",
                "permlevel": 1
            },
            {
                "fieldname": "is_work_shift_needed",
                "fieldtype": "Check",
                "label": "Is Shift Work Needed",
                "insert_after": "travel_required",
                "permlevel": 1
            },
            {
                "fieldname": "driving_license_needed",
                "fieldtype": "Check",
                "label": "Driving License Needed for this Position",
                "depends_on": "eval:doc.travel_required == 1",
                "insert_after": "is_work_shift_needed",
                "permlevel": 1
            },
            {
                "fieldname": "license_type",
                "fieldtype": "Link",
                "label": "License Type",
                "options": "License Type",
                "depends_on": "eval:doc.driving_license_needed == 1",
                "insert_after": "driving_license_needed",
                "permlevel": 1
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
                "label": "Preferred Educational Qualification",
                'options':"Educational Qualifications",
                "insert_after": "education",
                "permlevel": 1
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
                "insert_after": "education_column_break",
                "permlevel": 1
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
                "insert_after": "min_experience",
                "permlevel": 1
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
                "insert_after": "job_description_tab",
                "permlevel": 1
            },
            {
                "fieldname": "request_for",
                "label": "Request For",
                "fieldtype": "Select",
                "options": "Employee Replacement\nExisting Vacancy\nNew Vacancy",
                "insert_after": "naming_series"
            },
            {
                "fieldname": "employee_left",
                "label": "Employees Who Replaced",
                "fieldtype": "Link",
                "options": "Employee",
                "insert_after": "request_for",
                "depends_on": "eval:doc.request_for == 'Employee Replacement'"
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
                "insert_after": "interview",
                "permlevel": 1
            },

             {
                "fieldname": "location",
                "label": "Preferred Location",
                "fieldtype": "Link",
                "options": "Location",
                "insert_after": "employment_type",
                "permlevel": 1
            },
            {
                "fieldname": "job_title",
                "fieldtype": "Data",
                "label": "Job Title",
                "insert_after": "job_description_template",
                "reqd": 1,
            },
            {
                "fieldname": "suggested_designation",
                "fieldtype": "Link",
                "label": "Suggested Designation",
                "options": "Designation",
                "insert_after": "request_for",
                "permlevel": 2,
                "depends_on": "eval:doc.request_for == 'New Vacancy'"
            },
            {
                "fieldname": "suggestions",
                "fieldtype": "Small Text",
                "label": "Suggestions/Feedback",
                "insert_after": "suggestions_details_section",
                "permlevel": 3
            },
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
                "insert_after": "details_column_break",
                "permlevel": 1
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
                "insert_after": "applicant_interview_rounds"
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
                "fieldname": "applicant_interview_rounds",
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
        Custom fields that need to be added to the Job Opening Doctype
    '''
    return {
        "Job Opening": [
            {
                "fieldname": "job_details",
                "fieldtype": "Section Break",
                "label": "Job Details",
                "insert_after": "location"
            },
            {
                "fieldname": "no_of_positions",
                "fieldtype": "Int",
                "label": "No of.Positions",
                "insert_after": "employment_type"
            },
            {
                "fieldname": "no_of_days_off",
                "fieldtype": "Int",
                "label": "Number of Days Off",
                "insert_after": "job_details",
                "non_negative": 1
            },
            {
                "fieldname": "preffered_location",
                "label": "Preffered Location",
                "fieldtype": "Link",
                "options": "Location",
                "insert_after": "no_of_days_off"
            },
            {
                "fieldname": "job_details_column_break",
                "fieldtype": "Column Break",
                "label": "",
                "insert_after": "preffered_location"
            },
            {
                "fieldname": "travel_required",
                "fieldtype": "Check",
                "label": "Travel required for the position",
                "insert_after": "job_details_column_break"
            },
            {
                "fieldname": "driving_license_needed",
                "fieldtype": "Check",
                "label": "Driving License Needed for this Position",
                "depends_on": "eval:doc.travel_required == 1",
                "insert_after": "travel_required"
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
                "fieldname": "is_work_shift_needed",
                "fieldtype": "Check",
                "label": "Is Shift Work Needed",
                "insert_after": "license_type"
            },
            {
                "fieldname": "qualification_details",
                "fieldtype": "Section Break",
                "label": "Education and Qualification Details",
                "insert_after": "license_type",
            },
            {
               "fieldname": "min_education_qual",
                "fieldtype": "Table MultiSelect",
                "label": "Preferred Educational Qualification",
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
                "fieldname": "proficiency_break",
                "fieldtype": "Section Break",
                "label": "",
                "insert_after": "min_experience"
            },
            {
                "fieldname": "language_proficiency",
                "fieldtype": "Table",
                "options": "Language Proficiency",
                "label": "Language Proficiency",
                "insert_after": "proficiency_break",
                "description": "Proficency selected here is the minimum proficency needed"
            },
            {
                "fieldname": "skill_proficiency",
                "fieldtype": "Table",
                "options": "Skill Proficiency",
                "label": "Skill Proficiency",
                "insert_after": "language_proficiency",
                "description": "Proficency selected here is the minimum proficency needed"
            },
            {
                "fieldname": "interview_details_sb",
                "fieldtype": "Section Break",
                "label": "Interview Details",
                "insert_after": "skill_proficiency"
            },
            {
               "fieldname": "interview_rounds",
                "fieldtype": "Table MultiSelect",
                "label": "Interview Rounds",
                'options':"Interview Rounds",
                "insert_after": "interview_details_sb"
            }
        ]
    }

def get_company_custom_fields():
    '''
        Custom fields that need to be added to the Company Doctype
    '''
    return {
        "Company": [
            {
                "fieldname": "company_policy_tab",
                "fieldtype": "Tab Break",
                "label": "Company Policy",
                "insert_after": "dashboard_tab"
            },
            {
                "fieldname": "company_policy",
                "fieldtype": "Text Editor",
                "label": "Company Policy",
                "insert_after": "company_policy_tab"
            }
        ]
    }

def get_employee_performance_feedback():
    '''Custom fields that need to be added to
        Employee Performance Feedback doctype
    '''
    return  {
        "Employee Performance Feedback" : [
        {
            "fieldname": "employee_section",
            "fieldtype": "Section Break",
            "label": "",
            "insert_after": "feedback_ratings"
        },
        {
            "fieldname": "employee_total_score",
            "fieldtype": "Float",
            "label": "Total Score",
            "insert_after": "employee_section"
        },
        {
            "fieldname": "employee_column",
            "fieldtype": "Column Break",
            "label": "",
            "insert_after": "employee_total_score"
        },
        {
            "fieldname": "employee_average_score",
            "fieldtype": "Float",
            "label": "Average Score",
            "insert_after": "employee_column"
        },
        {
            "fieldname": "emp_section",
            "fieldtype": "Section Break",
            "label": "",
            "insert_after": "employee_average_score"
        },
        {
            "fieldname": "company_criteria",
            "fieldtype": "Table",
            "options": "Employee Feedback Rating",
            "label": "Company Criteria",
            "insert_after": "emp_section"
        },
        {
            "fieldname": "company_section",
            "fieldtype": "Section Break",
            "label": "",
            "insert_after": "company_criteria"
        },
        {
            "fieldname": "company_total_score",
            "fieldtype": "Float",
            "label": "Total Score",
            "insert_after": "company_section"
        },
        {
            "fieldname": "company_column",
            "fieldtype": "Column Break",
            "label": "",
            "insert_after": "company_total_score"
        },
        {
            "fieldname": "company_average_score",
            "fieldtype": "Float",
            "label": "Average Score",
            "insert_after": "company_column"
        },
        {
            "fieldname": "dept_section",
            "fieldtype": "Section Break",
            "label": "",
            "insert_after": "company_average_score"
        },
        {
            "fieldname": "department_criteria",
            "fieldtype": "Table",
            "options": "Employee Feedback Rating",
            "label": "Department Criteria",
            "insert_after": "dept_section"
        },
        {
            "fieldname": "dept_section1",
            "fieldtype": "Section Break",
            "label": "",
            "insert_after": "department_criteria"
        },
        {
            "fieldname": "department_total_score",
            "fieldtype": "Float",
            "label": "Total Score",
            "insert_after": "dept_section1"
        },
        {
            "fieldname": "dept_column",
            "fieldtype": "Column Break",
            "label": "",
            "insert_after": "department_total_score"
        },
        {
            "fieldname": "department_average_score",
            "fieldtype": "Float",
            "label": "Average Score",
            "insert_after": "dept_column"
        }
        ]
     }

def get_leave_type_custom_fields():
    '''
        Custom fields that need to be added to the Leave Type Doctype
     '''
    return {
        "Leave Type": [
            {
                "fieldname": "min_advance_days",
                "fieldtype": "Int",
                "label": "Minimum Advance Days",
                "description": "Specifies the minimum number of days required to apply for this leave.",
                "insert_after": "max_continuous_days_allowed"
            },
            {
               "fieldname": "is_proof_document",
               "fieldtype": "Check",
               "label": "Is Proof Document Required",
               "insert_after": "is_optional_leave"

            },
            {
              "fieldname": "medical_leave_required",
               "fieldtype": "Float",
               "label": "Medical Leave Required for Days",
               "depends_on": "eval:doc.is_proof_document",
               "insert_after": "is_proof_document"
            },
            {
               "fieldname": "allow_in_notice_period",
               "fieldtype": "Check",
               "label": "Allow in Notice Period",
               "insert_after": "is_compensatory"

            }
        ]
    }

def get_employee_separation_custom_fields():
    '''
    Custom fields that need to be added to the Employee Separation Doctype
    '''
    return {
        "Employee Separation": [
            {
                "fieldname": "employee_clearance",
                "fieldtype": "Table",
                "label": "Employee Clearance",
                "options": "Employee Clearance",
                "insert_after": "activities"

            },
            {
                "fieldname": "employee_exit_status",
                "fieldtype": "Select",
                "label": "Employee Exit Clearance Status",
                "options":"Pending\nCompleted",
                "insert_after": "employee_clearance"
            }
        ]
    }

def get_appraisal_template_custom_fields():
    '''
    Custom fields that need to be added to the Appraisal Template doctype
    '''
    return {
        "Appraisal Template": [
            {
                "fieldname": "department_rating_criteria",
                "fieldtype": " Table",
                "options": "Employee Feedback Rating",
                "label": "Department Rating Criteria",
                "insert_after": "rating_criteria"
            },
            {
                "fieldname": "company_rating_criteria",
                "fieldtype": " Table",
                "options": "Employee Feedback Rating",
                "label": "Company Rating Criteria",
                "insert_after": "label_for_department_kra"
            },
            {
                "fieldname": "label_for_department_kra",
                "fieldtype": "Data",
                "label": "Label for Department KRA",
                "insert_after": "department_rating_criteria"
            },
            {
                "fieldname": "label_for_company_kra",
                "fieldtype": "Data",
                "label": "Label for Company KRA",
                "insert_after": "company_rating_criteria"
            },
            {
                "fieldname": "designation_section",
                "fieldtype": "Section Break",
                "label": "",
                "insert_after": "label_for_company_kra"
            },
            {
                "fieldname": "assessment_officers",
                "fieldtype": "Table",
                "options": "Assessment Officer",
                "label": "Assessment Officers",
                "insert_after": "designation_section"
            }
        ]
    }

def get_employee_feedback_rating_custom_fields():
    '''
    Custom fields that need to be added to the Employee Feedback Rating doctype
    '''
    return {
        "Employee Feedback Rating": [
            {
                "fieldname": "marks",
                "fieldtype": " Float",
                "label": "Marks out of 5",
                "in_list_view":1,
                "insert_after": "rating"
            }
        ]
    }

def get_appraisal_custom_fields():
    '''
    Custom fields that need to be added to the Appraisal doctype
    '''
    return {
        "Appraisal": [
            {
                "fieldname": "appraisal_summary_tab_break",
                "fieldtype": "Tab Break",
                "label": "Appraisal Summary",
                "insert_after": "amended_from"
            },
            {
                "fieldname": "appraisal_summary",
                "fieldtype": "HTML",
                "label": "Appraisal Summary",
                "insert_after": "appraisal_summary_tab_break"
            },
            {
				"fieldname": "final_assesment_tab_break",
				"fieldtype": "Tab Break",
				"label": "Final Assesment",
				"insert_after": "appraisal_summary"
			},
			{
				"fieldname": "category_html",
				"fieldtype": "HTML",
				"label": "Appraisal Summary",
				"insert_after": "final_assesment_tab_break"
			},
        	{
				"fieldname": "category_based_on_marks",
				"fieldtype": "Link",
                "options": "Category",
				"label": "Category based on marks",
				"insert_after": "category_html",
                "read_only": 1
			},
			{
				"fieldname": "category_details",
				"fieldtype": "Table",
				"label": "Category Details",
				"options": "Category Details",
				"insert_after": "category_based_on_marks",
				"allow_on_submit": 1,
                "read_only": 1
			},
            {
                "fieldname": "employee_self_kra_rating",
                "fieldtype": "Table",
                "label": "Employee Rating",
                "options": "Employee Feedback Rating",
                "insert_after": "self_score",
            },
            {
                "fieldname": "total_employee_self_kra_rating",
                "fieldtype": "Float",
                "label": "Total Employee Self Score",
                "insert_after": "employee_self_kra_rating",
                "read_only": 1
            },
            {
                "fieldname": "avg_employee_self_kra_rating",
                "fieldtype": "Float",
                "label": "Average Employee Self Score",
                "insert_after": "total_employee_self_kra_rating",
                "read_only": 1
            },
            {
                "fieldname": "dept_self_kra_rating",
                "fieldtype": "Table",
                "label": "Department Rating",
                "options": "Employee Feedback Rating",
                "insert_after": "avg_employee_self_kra_rating",
            },
            {
                "fieldname": "total_dept_self_kra_rating",
                "fieldtype": "Float",
                "label": "Total Department Self Score",
                "insert_after": "dept_self_kra_rating",
                "read_only": 1
            },
            {
                "fieldname": "avg_dept_self_kra_rating",
                "fieldtype": "Float",
                "label": "Average Department Self Score",
                "insert_after": "total_dept_self_kra_rating",
                "read_only": 1
            },
            {
                "fieldname": "company_self_kra_rating",
                "fieldtype": "Table",
                "label": "Company Rating",
                "options": "Employee Feedback Rating",
                "insert_after": "avg_dept_self_kra_rating",
            },
            {
                "fieldname": "total_company_self_kra_rating",
                "fieldtype": "Float",
                "label": "Total Company Self Score",
                "insert_after": "company_self_kra_rating",
                "read_only": 1
            },
            {
                "fieldname": "avg_company_self_kra_rating",
                "fieldtype": "Float",
                "label": "Average Company Self Score",
                "insert_after": "total_company_self_kra_rating",
                "read_only": 1
            },
            {
                "fieldname": "final_average_score",
                "fieldtype": "Float",
                "label": "Final Average Score",
                "insert_after": "employee_image"
            }
        ]
    }

def get_appraisal_kra_custom_fields():
	'''
	Custom fields that need to be added to the Appraisal KRA doctype
	'''
	return {
		"Appraisal KRA":[
            {
                "fieldname": "kra_goals",
                "fieldtype": "Text Editor",
                "label": "Goals",
                "insert_after": "goal_score",
                "in_list_view":1
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
            "doc_type": "Appraisal Template",
            "field_name": "rating_criteria",
            "property": "label",
            "value": "Employee Criteria"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Feedback Rating",
            "field_name": "rating_criteria",
            "property": "read_only",
            "property_type": "Table",
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
            "doc_type": "Leave Allocation",
            "field_name": "to_date",
            "property": "allow_on_submit",
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
            "doc_type": "Quotation",
            "field_name": "scan_barcode",
            "property": "hidden",
            "property_type": "Data",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Quotation",
            "field_name": "shipping_rule",
            "property": "hidden",
            "property_type": "Link",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Quotation",
            "field_name": "incoterm",
            "property": "hidden",
            "property_type": "Link",
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
            "value": "Open\nReplied\nRejected\nShortlisted from Interview\nLocal Enquiry Started\nLocal Enquiry Completed\nLocal Enquiry Rejected\nLocal Enquiry Approved\nSelected\nHold\nAccepted\nTraining Completed\nJob Proposal Created\nJob Proposal Accepted\nInterview Scheduled\nInterview Ongoing\nInterview Completed\nShortlisted\nPending Document Upload\nDocument Uploaded"
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
            "doctype_or_field": "DocField",
            "doc_type": "Leave Application",
            "field_name": "posting_date",
            "property": "read_only",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "status",
            "property": "options",
            "value": "Pending\nOpen & Approved\nRejected\nOn Hold\nCancelled"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Event",
            "field_name": "event_category",
            "property": "options",
            "value": "Event\nMeeting\nCall\nSent/Received Email\nOne to One Meeting\nOther"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Opening",
            "field_name": "location",
            "property": "hidden",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Boarding Activity",
            "field_name": "required_for_employee_creation",
            "property": "hidden",
            "property_type": "Check",
            "value":1
        },
        {
            "doctype_or_field":"DocField",
            "doc_type": "Attendance Request",
            "field_name": "reason",
            "property": "options",
            "value": "\nWork From Home\nOn Duty\nOn Deputation\nForgot to Checkin\nForgot to Checkout\nPermitted Late Arrival\nPermitted Early Exit"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Skill Assessment",
            "field_name": "rating",
            "property": "reqd",
            "property_type": "Check",
            "value":0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Skill Assessment",
            "field_name": "rating",
            "property": "read_only",
            "property_type": "Check",
            "value":1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee External Work History",
            "field_name": "designation",
            "property": "label",
            "value":"Designation At The Time Of Joining"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "designation",
            "property": "fetch_from",
            "property_type": "Link",
            "value":"employee_left.designation"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "department",
            "property": "fetch_from",
            "property_type": "Link",
            "value":"employee_left.department"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Performance Feedback",
            "field_name": "total_score",
            "property": "hidden",
            "property_type": "Float",
            "value":1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Feedback Rating",
            "field_name": "Rating",
            "property": "read_only",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Performance Feedback",
            "field_name": "feedback_ratings",
            "property": "label",
            "property_type": "Table",
            "value":"Employee Criteria"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal",
            "field_name": "rate_goals_manually",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal",
            "field_name": "goal_score_percentage",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal",
            "field_name": "total_score",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal KRA",
            "field_name": "goal_completion",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal KRA",
            "field_name": "goal_score",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Employee Feedback Rating",
            "field_name": "rating",
            "property": "read_only",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal",
            "field_name": "goals",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal",
            "field_name": "appraisal_kra",
            "property": "label",
            "property_type": "Table",
            "value":"KRA's",
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "designation",
            "property": "reqd",
            "property_type": "Check",
            "value": 0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Applicant",
            "field_name": "resume_link",
            "property": "hidden",
            "property_type": "Data",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal",
            "field_name": "self_ratings",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Appraisal",
            "field_name": "self_score",
            "property": "hidden",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Budget",
            "field_name": "monthly_distribution",
            "property": "hidden",
            "property_type": "Link",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "designation",
            "property": "reqd",
            "property_type": "Check",
            "value": 0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Vehicle",
            "field_name": "insurance_details",
            "property": "hidden",
            "property_type": "Section Break",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Interview",
            "field_name": "resume_link",
            "property": "hidden",
            "property_type": "",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "HR Settings",
            "field_name": "emp_created_by",
            "property": "depends_on",
            "property_type": "Code",
            "value": "eval: doc.employee_naming_by_department === 0 "
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Budget Account",
            "field_name": "account",
            "property": "read_only",
            "property_type": "Link",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "no_of_positions",
            "property": "reqd",
            "property_type": "Check",
            "value": 0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "expected_compensation",
            "property": "reqd",
            "value": 0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "expected_compensation",
            "property": "default",
            "value": 0.0
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "expected_compensation",
            "property": "mandatory_depends_on",
            "value": "eval: frappe.user_roles.includes('HR Manager')"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "expected_compensation",
            "property": "depends_on",
            "value": "eval: frappe.user_roles.includes('HR Manager')"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "employee_left",
            "property": "ignore_user_permissions",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "requested_by",
            "property": "ignore_user_permissions",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Shift Assignment",
            "field_name": "swap_with_employee",
            "property": "ignore_user_permissions",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Shift Assignment",
            "field_name": "employee",
            "property": "ignore_user_permissions",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "department",
            "property": "reqd",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "section_break_7",
            "property": "collapsible",
            "property_type": "Check",
            "value": 1
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": "designation",
            "property": "depends_on",
            "value": "eval: !(doc.workflow_state == 'Draft' && doc.request_for == 'New Vacancy')"
        },
        {
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "property": "field_order",
            "value": "[\"naming_series\", \"designation\", \"department\", \"column_break_qkna\", \"no_of_positions\", \"expected_compensation\",\"reason_for_requesting\", \"column_break_4\", \"company\", \"status\", \"section_break_7\", \"requested_by\", \"requested_by_name\", \"column_break_10\", \"requested_by_dept\", \"requested_by_designation\", \"timelines_tab\", \"posting_date\", \"completed_on\", \"column_break_15\", \"expected_by\", \"time_to_fill\", \"job_description_tab\", \"description\", \"connections_tab\"]"
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
                "fieldname": "region",
                "fieldtype": "Link",
                "label": "Region",
                "options": "Region",
                "insert_after": "is_reverse_charge"
            },
            {
                "fieldname": "executive",
                "fieldtype": "Link",
                "label": "Executive",
                "options": "Employee",
                "insert_after": "delivery_date"
            },
            {
                "fieldname": "executive_name",
                "fieldtype": "Data",
                "label": "Executive Name",
                "fetch_from": "executive.employee_name",
                "insert_after": "executive",
                "read_only": 1
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
                "insert_after":"skill",
                "in_list_view": 1
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
                "label": "Weight",
                "insert_after":"remarks"
            }
        ]
    }

def get_training_event_employee_custom_fields():
    '''
    Custom fields to be added to the Training Event Employee Doctype
    '''
    return {
        "Training Event Employee": [
              {
                    "fieldname": "training_request",
                    "fieldtype": "Link",
                    "label": "Training Request",
                    "options": "Training Request",
                    "insert_after": "employee_name",
                    "in_list_view": 1,
                    "width": 2
              }
        ]
    }

def get_beams_roles():
    '''
        Method to get BEAMS specific roles
    '''
    return ['Production Manager', 'CEO', 'Company Secretary', 'HOD','Enquiry Officer','Enquiry Manager','Shift Publisher','Program Producer','Operations Head','Operations User','Admin','Driver','Budget User','Technical Store Head']

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
        },
        {
            'doctype': 'Translation',
            'source_text':'Attendance Request',
            'translated_text':'Attendance Regularisation',
            'language':'en'
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

def get_employment_type():
    '''
    Custom fields to be added to the Employment Type Doctype
    '''
    return {
        "Employment Type": [
            {
                "fieldname": "notice_period",
                "fieldtype": "Int",
                "label": "Notice Period",
                "insert_after": "employment_type"
            }
        ]
    }

def get_appointment_letter():
    '''
    Custom fields that need to be added to the Appointment Letter DocType
    '''
    return {
        "Appointment Letter": [
            {
                "fieldname": "notice_period",
                "fieldtype": "Int",
                "label": "Notice Period",
                "insert_after": "applicant_name"
            }
        ]
    }

def get_vehicle_custom_fields():
    '''
    Custom fields that need to be added to the Vehicle DocType
    '''
    return {
        "Vehicle": [
        {
            "fieldname": "vehicle_section_break",
            "fieldtype": "Section Break",
            "label": "Vehicle Details",
            "insert_after": "doors"
        },
        {
            "fieldname": "vehicle_documents",
            "fieldtype": "Table",
            "label": "Vehicle Documents",
            "options": "Vehicle Documents",
            "insert_after": "vehicle_section_break"
        }
        ]
    }

def get_hr_settings_custom_fields():
    '''
        Custom fields that need to be added to the HR Settings DocType
    '''
    return {
        "HR Settings": [
            {
                "fieldname": "employee_naming_by_department",
                "fieldtype": "Check",
                "label": "Employee Naming By Department",
                "insert_after": "employee_settings"
            }
        ]
    }

def get_asset_category_custom_fields():
    '''
        Custom fields that need to be added to the Asset Category DocType
    '''
    return {
        "Asset Category": [
            {
                "fieldname": "parent_asset_category",
                "fieldtype": "Link",
                "label": "Parent Asset Category",
                "options": "Asset Category",
                "insert_after": "asset_category_name"
            }
        ]
    }
