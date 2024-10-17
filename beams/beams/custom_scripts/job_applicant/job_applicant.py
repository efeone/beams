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
    Method triggered before the documentaion saving .
    Validate the Job Applicant against Job Opening requirements.
    """
    if not frappe.db.exists("Job Opening", {"name": doc.job_title}):
        frappe.throw(_("The specified Job Opening does not exist."))
    job_opening = frappe.get_doc('Job Opening', doc.job_title)

    if doc.location != job_opening.location:
        frappe.throw(_("Applicant's location does not match the Job Opening's location."))

    applicant_qualifications = [qual.qualification for qual in doc.min_education_qual] if doc.min_education_qual else []
    job_opening_qualifications = [qual.qualification for qual in job_opening.min_education_qual] if job_opening.min_education_qual else []
    if not any(qual in job_opening_qualifications for qual in applicant_qualifications):
        frappe.throw(_("Applicant's  does not meet the minimum qualification for the Job Opening"))

    if doc.min_experience < job_opening.min_experience:
        frappe.throw(_("Applicant's does not meet the minimum experience  for the Job Opening."))

    required_skills = {skill.skill: skill.proficiency for skill in job_opening.skill_proficiency}
    applicant_skills = {skill.skill: skill.proficiency for skill in doc.skill_proficiency}
    missing_skills = []
    proficiency_mismatch = []
    for required_skill, required_proficiency in required_skills.items():
        if required_skill not in applicant_skills:
            missing_skills.append(required_skill)
        else:
            applicant_proficiency = applicant_skills[required_skill]
            if applicant_proficiency < required_proficiency:
                proficiency_mismatch.append(f"{required_skill} (Required: {required_proficiency}, Provided: {applicant_proficiency})")
    if missing_skills:
        frappe.throw(_("The Applicant's does not meet the skill requirements for the Job Opening."))
    if proficiency_mismatch:
        frappe.throw(_("Applicant's does not meet the required proficiency levels for the following skills"))
