import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
# Create a Company Policy Acceptance Log  Document by mapping fields from employee onboarding
def create_cpal(source_name):
    # Get the Employee Onboarding document
    onboarding_doc = frappe.get_doc('Employee Onboarding', source_name)

    # Check if a CPAL already exists for this Employee Onboarding document
    existing_cpal = frappe.db.get_value('Company Policy Acceptance Log',
                                        {'employee': onboarding_doc.employee, 'company': onboarding_doc.company},
                                        'name')

    if existing_cpal:
        # If a CPAL already exists, return the existing CPAL document name
        return existing_cpal

    # Fetch the company_policy from the Company doctype
    company_policy = frappe.db.get_value('Company', onboarding_doc.company, 'company_policy')
    if not frappe._strip_html_tags(company_policy):
        frappe.throw(f"Please set the <b>Company Policy</b> in the Company <b>{onboarding_doc.company}</b> to create the  <b>Company Policy Acceptance Log</b>")

    # Create a mapped document using get_mapped_doc
    cpal_doc = get_mapped_doc(
        "Employee Onboarding",
        source_name,
        {
            "Employee Onboarding": {
                "doctype": "Company Policy Acceptance Log",
                "field_map": {
                    "employee": "employee",
                    "employee_name": "employee_name",
                    "department": "department",
                    "date_of_joining": "date_of_joining",
                    "company": "company"
                }
            }
        }
    )
    cpal_doc.insert(ignore_permissions=True)
    return cpal_doc.name

@frappe.whitelist()
def get_employee_details(employee_id):
        employee = frappe.get_doc('Employee', employee_id)
        return {
            'department': employee.department,
            'designation': employee.designation,
            'date_of_joining': employee.date_of_joining,
            'holiday_list': employee.holiday_list,
            'employee_grade': employee.grade
        }

@frappe.whitelist()
def get_excluded_job_applicants():
    # Get job applicants linked to active employees
    job_applicants_with_active_employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "job_applicant": ["!=", ""]},
        pluck="job_applicant"
    )

    # Get job applicants linked to Employee Onboarding (excluding canceled)
    job_applicants_with_onboarding = frappe.get_all(
        "Employee Onboarding",
        filters={"docstatus": ["!=", 2]},
        pluck="job_applicant"
    )

    # Get applicants who satisfy **both** conditions
    excluded_applicants = list(set(job_applicants_with_active_employees) & set(job_applicants_with_onboarding))

    return excluded_applicants if excluded_applicants else []
