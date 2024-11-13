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

    # Insert the new CPAL document into the database
    cpal_doc.insert(ignore_permissions=True)

    # Return the name of the created CPAL document
    return cpal_doc.name
