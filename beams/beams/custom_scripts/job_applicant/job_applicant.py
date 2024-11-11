import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url, now_datetime
from frappe.utils import nowdate
from frappe.utils import get_url_to_form
from frappe.utils.password import encrypt


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

    # Check if job_title is specified and fetch the Job Opening
    if not doc.job_title:
        return

    job_opening = frappe.get_doc('Job Opening', doc.job_title)

    # Ensure the Job Opening exists
    if not job_opening:
        frappe.throw(_("Specified Job Opening '{0}' not found.").format(doc.job_title))
    if not doc.min_education_qual:
        frappe.throw(_("Applicant's Educational Qualification is required."))

    # Validate education qualification only if it's filled in the Job Opening
    applicant_qualification = doc.min_education_qual
    job_opening_qualifications = [qual.qualification for qual in job_opening.min_education_qual] if job_opening.min_education_qual else []
    if job_opening_qualifications and applicant_qualification not in job_opening_qualifications:
        required_qualifications = ", ".join(job_opening_qualifications)
        frappe.throw(_("Applicant does not match Educational qualifications required: {0}").format(required_qualifications))

    # Validate experience only if it's filled in the Job Opening
    if doc.min_experience is None:
        frappe.throw(_("Applicant's experience is not provided."))

    if job_opening.min_experience is None:
        frappe.throw(_("The job's required experience is not specified."))

    if doc.min_experience < job_opening.min_experience:
        frappe.throw(_("Applicant does not meet the required experience: {0} years").format(job_opening.min_experience))

    if not doc.skill_proficiency:
        frappe.throw(_("Applicant's skills are required."))

    # Validate skills only if required skills are filled in the Job Opening
    required_skills = {skill.skill for skill in job_opening.skill_proficiency}
    applicant_skills = {skill.skill for skill in doc.skill_proficiency}
    if required_skills and (missing_skills := required_skills - applicant_skills):
        required_skills_list = ", ".join(required_skills)
        frappe.throw(_("The Applicant does not meet the Required skills: {0}").format(required_skills_list))


@frappe.whitelist()
def get_existing_local_enquiry_report(doc_name):
    """
    Create a Local Enquiry Report if it doesn't already exist.

    """

    # Check if a Local Enquiry Report already exists for the given Job Applicant
    report_exists = frappe.db.exists("Local Enquiry Report", {"job_applicant": doc_name})
    if report_exists:
        report_doc = frappe.get_doc("Local Enquiry Report", report_exists)
        return report_doc.name  # Return the report name if it exists
    return "no_report"  # Indicate no report exists

@frappe.whitelist()
def create_and_return_report(job_applicant):
    """
    Create a Local Enquiry Report, show an alert message, and return its name.

    """
    # Create a new Local Enquiry Report document
    new_report = frappe.get_doc({
        "doctype": "Local Enquiry Report",
        "job_applicant": job_applicant,
        # Set other required fields here if needed (e.g., status, date, etc.)
    })

    # Insert and save the new document into the database, ignoring permissions
    new_report.insert(ignore_permissions=True)
    new_report.save(ignore_permissions=True)
    frappe.msgprint(
        'Local Enquiry Report Created: <a href="{0}">{1}</a>'.format(
            get_url_to_form(new_report.doctype, new_report.name),
            new_report.name
        ),
        alert=True,
        indicator='green'
    )
    # Return the name of the newly created report for further use (e.g., navigation)
    return new_report.name

@frappe.whitelist()
def send_magic_link(applicant_id):
    """
    Sends a unique magic link to the specified job applicant's email for document upload.
    Args:
        applicant_name (str): The name of the job applicant.
    Returns:
        None
    """
    if frappe.db.exists('Job Applicant', applicant_id):
        doc = frappe.get_doc('Job Applicant', applicant_id)
        link = generate_magic_link(doc.name)
        if frappe.db.exists('Email Template', 'Job Applicant Follow Up'):
            template = frappe.get_doc('Email Template', 'Job Applicant Follow Up')
            subject = frappe.render_template(template.subject, {'applicant_name': doc.applicant_name})
            response = frappe.render_template(template.response, {
                'applicant_name': doc.applicant_name,
                'magic_link': link
            })
            frappe.sendmail(
                recipients=[doc.email_id],
                subject=subject,
                message=response
            )
            frappe.msgprint(f'Magic link sent to {doc.email_id}')
        else:
            frappe.msgprint('Email Template "Job Applicant Follow Up" does not exist.', alert=True)
    else:
        frappe.msgprint(f'Job Applicant with ID {applicant_id} does not exist.', alert=True)

def generate_magic_link(applicant_id):
    """
    Generates and returns a magic link URL for the specified job applicant
    Args:
        applicant_name (str): The name of the job applicant.
    Returns:
        str: The generated magic link URL.
    """
    link = f"{get_url()}/job_application_upload/upload_doc?applicant_id="
    if frappe.db.exists('Job Applicant', applicant_id):
        encrypted_link = encrypt(applicant_id)
        link += encrypted_link
    return link


@frappe.whitelist()
def fetch_interview_rounds(doc, method):
    """
    Fetch interview rounds for a job applicant based on the job title.
    If the applicant has a job title and no interview rounds have been added,
    this function retrieves the job requisition linked to the job opening
    and populates the interview rounds in the applicant's document.
    """
    if doc.job_title and not doc.applicant_interview_round:  # Check if job title exists and rounds have not been added
        if frappe.db.exists('Job Opening', doc.job_title):  # Check if the job opening exists
            job_opening = frappe.get_doc('Job Opening', doc.job_title)
            if job_opening.job_requisition and frappe.db.exists('Job Requisition', job_opening.job_requisition):
                job_requisition = frappe.get_doc('Job Requisition', job_opening.job_requisition)
                if job_requisition.interview_rounds:
                    existing_rounds = {round.interview_round for round in doc.applicant_interview_round}
                    for round in job_requisition.interview_rounds:
                        if round.interview_round not in existing_rounds:
                            doc.append('applicant_interview_round', {
                                'interview_round': round.interview_round
                            })

@frappe.whitelist()
def fetch_location_from_job_opening(job_title, willing_to_work_on_location):
    """
    Fetches location from Job Opening if the checkbox is checked and job_title is provided.
    """
    if willing_to_work_on_location and job_title:
        # Fetch the location from the linked Job Opening
        location = frappe.db.get_value('Job Opening', job_title, 'location')
        if location:
            return location
    return None
