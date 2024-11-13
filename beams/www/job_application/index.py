import frappe
import json
from frappe.utils import escape_html

@frappe.whitelist(allow_guest=True)
def submit_job_application(applicant_name, email_id, phone_number, min_experience=None, min_education_qual=None, job_title=None, location=None, resume_attachment=None, skill_proficiency=None):
    # Create a new Job Applicant document
    job_applicant = frappe.get_doc({
        "doctype": "Job Applicant",
        "applicant_name": applicant_name,
        "email_id": email_id,
        "phone_number": phone_number,
        "min_experience": min_experience,
        "min_education_qual": min_education_qual,
        "job_title": job_title,
        "location": location,
        "resume_attachment": resume_attachment,
    })

    print("value in skill", skill_proficiency)

    # Process skills if provided
    if skill_proficiency:

        print("got skill")

        try:
            skills_data = json.loads(skill_proficiency)  # Convert JSON to Python list

            # Append skills to the child table
            for skill_data in skills_data:
                child = job_applicant.append("skill_proficiency", {})  # Replace "skills" with your actual child table fieldname
                child.skill = skill_data.get("skill")
                child.proficiency = skill_data.get("rating")
        except json.JSONDecodeError:
            frappe.throw("Invalid JSON format for skills data")

    # Insert the document into the database
    # job_applicant.flags.ignore_mandatory = True
    job_applicant.insert()
    # frappe.db.commit()

    # Return a success message
    return {"message": "Job application submitted successfully"}
