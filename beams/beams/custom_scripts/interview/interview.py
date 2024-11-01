import frappe
from frappe import _

@frappe.whitelist()
def create_interview_feedback(data, interview_name, interviewer, job_applicant):
    """
    method: Creates and submits an Interview Feedback document for a job applicant, ensuring the user is the interviewer, validates skills and their scores, and appends them to the feedback.
    """
    import json

    # Parse the incoming data
    if isinstance(data, str):
        data = frappe._dict(json.loads(data))

    # Check if the current user is the interviewer
    if frappe.session.user != interviewer:
        frappe.throw(_("Only Interviewers are allowed to submit Interview Feedback"))

    # Create a new Interview Feedback document
    interview_feedback = frappe.new_doc("Interview Feedback")
    interview_feedback.interview = interview_name
    interview_feedback.interviewer = interviewer
    interview_feedback.job_applicant = job_applicant

    # Ensure skill_set is provided
    if not hasattr(data, 'skill_set') or not data.skill_set:
        frappe.throw(_("No skills found in the feedback data."))

    # Append skills directly with the score as the rating
    for d in data.skill_set:
        d = frappe._dict(d)

        # Ensure the score is not None and is a valid number
        if d.score is None or d.score == '':
            frappe.throw(_("Score for skill {0} is missing or invalid.").format(d.skill))

        try:
            # Convert score to integer
            rating = int(d.score)/10
        except ValueError:
            frappe.throw(_("Invalid score for skill {0}. Please enter a valid number.").format(d.skill))


        # Append the validated skill and rating to the Interview Feedback
        interview_feedback.append("skill_assessment", {"skill": d.skill, "rating": rating, "score":d.score})

    # Set feedback and result
    interview_feedback.remarks = data.remarks
    interview_feedback.result = data.result

    # Save and submit the feedback document
    interview_feedback.save()
    interview_feedback.submit()

    # Show success message with a link to the created feedback
    frappe.msgprint(
        _("Interview Feedback {0} submitted successfully").format(
            frappe.utils.get_link_to_form("Interview Feedback", interview_feedback.name)
        )
    )
