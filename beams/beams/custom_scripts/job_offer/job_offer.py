import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
    def set_missing_values(source, target):
        # Fetch personal email and applicant name from Job Applicant
        target.personal_email, target.first_name = frappe.db.get_value(
            "Job Applicant", source.job_applicant, ["email_id", "applicant_name"]
        )

    # Map fields from Job Offer to Employee
    doc = get_mapped_doc(
        "Job Offer",
        source_name,
        {
            "Job Offer": {
                "doctype": "Employee",
                "field_map": {
                    "applicant_name": "employee_name",
                    "offer_date": "scheduled_confirmation_date",
                },
            }
        },
        target_doc,
        set_missing_values,
    )

    # Map additional fields from Job Applicant to Employee
    job_applicant = frappe.get_doc("Job Offer", source_name).job_applicant
    if job_applicant:
        applicant_data          = frappe.get_doc("Job Applicant", job_applicant)
        doc.gender              = applicant_data.gender
        doc.date_of_birth       = applicant_data.date_of_birth
        doc.cell_number         = applicant_data.current_mobile_no
        doc.name_of_father      = applicant_data.father_name
        doc.department          = applicant_data.department
        doc.designation         = applicant_data.designation
        doc.marital_status      = applicant_data.marital_status
        doc.permanent_address   = applicant_data.permanent_address
        doc.current_address     = applicant_data.current_address

    return doc
