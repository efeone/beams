import frappe
from frappe.utils import escape_html

@frappe.whitelist(allow_guest=True)
def create_job_applicant(first_name, father_name, date_of_birth, gender, marital_status, current_address,
                         current_period_from, current_period_to, current_residence_no, current_mobile_no,
                         permanent_address, permanen_period_from, permanent_period_to, permanent_residence_no,
                         permanent_email_id, email_id_1):
    try:
    # Log the received data
        frappe.log(f"Received data - First Name: {first_name}, Email: {email_id_1}")

    # Ensure required fields are present
        if not first_name or not current_mobile_no or not email_id_1:
            frappe.throw("Missing required fields")


        # Create Job Applicant doc
        doc = frappe.get_doc({
            'doctype': 'Job Applicant',
            'first_name': escape_html(first_name),
            'father_name': escape_html(father_name),
            'date_of_birth': escape_html(date_of_birth),
            'gender': escape_html(gender),
            'marital_status': escape_html(marital_status),
            'current_address': escape_html(current_address),
            'current_period_from': escape_html(current_period_from),
            'current_period_to': escape_html(current_period_to),
            'current_residence_no': escape_html(current_residence_no),
            'current_mobile_no': escape_html(current_mobile_no),
            'permanent_address': escape_html(permanent_address),
            'permanen_period_from': escape_html(permanen_period_from),
            'permanent_period_to': escape_html(permanent_period_to),
            'permanent_residence_no': escape_html(permanent_residence_no),
            'permanent_email_id': escape_html(permanent_email_id),
            'email_id_1': escape_html(email_id_1)
        })

        doc.insert()
        frappe.msgprint(f"Job Applicant {doc.name} created successfully.", indicator="green", alert=True)
        frappe.db.commit()

        return {"message": "success"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Application Submission Error")
        return {"message": str(e)}
