import frappe
from frappe import _

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)


    if "Administrator" in user_roles:
        return ""


    if "Interviewer" in user_roles:
        return f"""
        `tabJob Applicant`.name IN (
            SELECT reference_name
            FROM `tabToDo`
            WHERE reference_type = 'Job Applicant'
            AND allocated_to = '{user}'
        )
        """
    return None

@frappe.whitelist()
def validate(doc, method):
    """
    Method triggered before the document is saved.
    Validate the Job Applicant against Job Opening requirements.
    """
    if not frappe.db.exists("Job Opening", {"name": doc.job_title}):
        frappe.throw(_("The specified Job Opening does not exist."))
    job_opening = frappe.get_doc('Job Opening', doc.job_title)
    if doc.location != job_opening.location:
        frappe.throw(_("Applicant location does not match the desired location {0}").format(job_opening.location))
    applicant_qualification = doc.min_education_qual
    job_opening_qualifications = [qual.qualification for qual in job_opening.min_education_qual] if job_opening.min_education_qual else []
    if applicant_qualification not in job_opening_qualifications:
        required_qualifications = ", ".join(job_opening_qualifications)
        frappe.throw(_("Applicant does not match Educational qualifications required: {0}").format(required_qualifications))
    if doc.min_experience is None:
        frappe.throw(_("Applicant's experience is not provided."))

    if job_opening.min_experience is None:
        frappe.throw(_("The job's required experience is not specified."))

    if doc.min_experience < job_opening.min_experience:
        frappe.throw(_("Applicant does not meet the required experience: {0} years").format(job_opening.min_experience))

    if doc.min_experience < job_opening.min_experience:
        frappe.throw(_("Applicant does not meet the Required experience: {0} years").format(job_opening.min_experience))
    required_skills = {skill.skill for skill in job_opening.skill_proficiency}
    applicant_skills = {skill.skill for skill in doc.skill_proficiency}
    missing_skills = required_skills - applicant_skills
    if missing_skills:
        required_skills_list = ", ".join(required_skills)
        frappe.throw(_("The Applicant does not meet the Required skills: {0}").format(required_skills_list))

@frappe.whitelist()
def create_local_enquiry(doc_name):
    """
    Create a Local Enquiry Report if it doesn't already exist.

    Args:
        doc_name (str): The name of the Job Applicant.

    Returns:
        str: The name of the existing report if found, or the name of the newly created report.
    """

    # Check if a Local Enquiry Report already exists for the given Job Applicant
    report_exists = frappe.db.exists("Local Enquiry Report", {"job_applicant": doc_name})

    if report_exists:
        # Update the message to indicate that the report with the given name exists
        frappe.msgprint(_("Enquiry Report {0} already exists").format(report_exists))
        return report_exists  # Return the existing report name

    # Logic to create a new Local Enquiry Report
    new_report = frappe.new_doc("Local Enquiry Report")
    new_report.job_applicant = doc_name  # Set the job_applicant field to the name of the Job Applicant

    # Insert the new report
    new_report.insert(ignore_mandatory=True, ignore_permissions=True)

    return new_report.name  # Return the name of the newly created report
