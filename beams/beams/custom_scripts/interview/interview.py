import frappe
from frappe import _

@frappe.whitelist()
def create_interview_feedback(data, interview_name, interviewer, job_applicant, submit=0):
    """
    Creates an Interview Feedback document for a job applicant,
    allowing for draft saves and submission.
    """
    import json

    # Parse the incoming data
    if isinstance(data, str):
        data = frappe._dict(json.loads(data))

    # Check if the current user is the interviewer
    if frappe.session.user != interviewer:
        frappe.throw(_("Only Interviewers are allowed to submit Interview Feedback"))

    # Create a new Interview Feedback document
    interview_feedback_name = frappe.db.exists('Interview Feedback',{'interview':interview_name,'docstatus':0})

    if interview_feedback_name:
        interview_feedback = frappe.get_doc("Interview Feedback",interview_feedback_name)
    else:
        interview_feedback = frappe.new_doc("Interview Feedback")

    interview_feedback.interview = interview_name
    interview_feedback.interviewer = interviewer
    interview_feedback.job_applicant = job_applicant

    # Ensure skill_set is provided
    if not hasattr(data, 'skill_set') or not data.skill_set:
        frappe.throw(_("No skills found in the feedback data."))

    if interview_feedback_name:
        interview_feedback.skill_assessment = []
    # Append skills directly with the score as the rating
    for d in data.skill_set:
        d = frappe._dict(d)

        # Ensure the score is not None and is a valid number
        if d.score is None or d.score == '':
            frappe.throw(_("Score for skill {0} is missing or invalid.").format(d.skill))

        # Check if score is a number (int or float) and validate
        if not isinstance(d.score, (int, float)) or d.score < 0 or d.score > 100:
            frappe.throw(_("Score for skill {0} must be a number between 0 and 100.").format(d.skill))

        # Convert score to a float and calculate rating
        rating = float(d.score) / 10
        # Append the validated skill and rating to the Interview Feedback
        interview_feedback.append("skill_assessment", {
            "skill": d.skill,
            "rating": rating,
            "score": d.score
        })

    # Process question assessments if provided
    if hasattr(data, 'question_assessment') and data.question_assessment:
        if interview_feedback_name:
            interview_feedback.interview_question_result = []
        for q in data.question_assessment:
            q = frappe._dict(q)

            # Ensure the score is not None and is a valid number
            if q.score is None or q.score == '':
                frappe.throw(_("Score for question '{0}' is missing or invalid.").format(q.question))

            # Check if score is a number (int or float) and validate
            if not isinstance(q.score, (int, float)) or q.score < 0 or q.score > 100:
                frappe.throw(_("Score for question '{0}' must be a number between 0 and 100.").format(q.question))

            # Append the validated question, answer, and score to the Interview Feedback
            interview_feedback.append("interview_question_result", {
                "question": q.question,
                "answer": q.answer,
                "score": q.score  # Directly use the score
            })

    # Set feedback and result
    interview_feedback.feedback = data.feedback
    interview_feedback.result = data.result
    if int(submit):
        interview_feedback.submit()  # Submit if the submit flag is True
    else:
        interview_feedback.save()

    # Show success message with a link to the created feedback
    frappe.msgprint(
        _("Interview Feedback {0} {1} successfully").format(
            frappe.utils.get_link_to_form("Interview Feedback", interview_feedback.name),
            _("submitted") if int(submit) else _("saved")
        )
    )


@frappe.whitelist()
def get_interview_feedback(interview_name):
    """
    Fetch the existing Interview Feedback for the specified interview.

    :param interview_name: Name of the interview to fetch feedback for
    :return: Feedback data including skill assessments and question assessments, or None if not found
    """
    # Fetch the existing Interview Feedback
    feedback = frappe.get_all("Interview Feedback",
        filters={"interview": interview_name},
        fields=["name", "feedback", "result"])  # Ensure 'feedback' and 'result' are the correct fields

    if feedback:
        feedback = feedback[0]  # Get the first feedback if it exists

        # Fetching the skill assessments from the child table 'Skill Assessment'
        skill_set = frappe.get_all("Skill Assessment",
            filters={"parent": feedback.name},
            fields=["skill", "score"])  # Fetching skill and score fields

        # Fetching the question assessments from the child table 'Interview Question Result'
        question_assessments = frappe.get_all("Interview Question Result",
            filters={"parent": feedback.name},
            fields=["question", "answer", "score"])  # Fetching question, _answer, and score fields

        # Map the feedback to include all relevant fields
        feedback_data = {
            "name": feedback.name,
            "feedback": feedback.feedback,  # Mapping  to feedback
            "result": feedback.result,      # Mapping result
            "skill_set": [
                {"skill": set.skill, "score": set.score} for set in skill_set
            ],  # Including skill assessments with score mapped to rating
            "question_assessment": [
                {"question": assessment.question, "answer": assessment.answer, "score": assessment.score} for assessment in question_assessments
            ]  # Including question assessments with _answer mapped to answer
        }

        return feedback_data
    else:
        return None

@frappe.whitelist()
def on_interview_creation(doc, method):
    '''
    Set the Job Applicant's status to 'Interview Scheduled' when an Interview is created.
    '''
    if frappe.db.exists("Job Applicant", doc.job_applicant):
        job_applicant_doc = frappe.get_doc("Job Applicant", doc.job_applicant)
        if job_applicant_doc.status != "Interview Scheduled":
            job_applicant_doc.status = "Interview Scheduled"
            job_applicant_doc.save()

def update_applicant_interview_round(doc, method):
    '''
    Update the Applicant Interview Round child table in Job Applicant with interview reference and status on creation.
    '''
    if doc.job_applicant and doc.interview_round:
        # Check if the Job Applicant exists
        if not frappe.db.exists("Job Applicant", doc.job_applicant):
            frappe.msgprint(f"Job Applicant {doc.job_applicant} does not exist.")
            return

        job_applicant_doc = frappe.get_doc("Job Applicant", doc.job_applicant)

        # Find the corresponding interview round in the Job Applicant's applicant_interview_round table
        for interview_round in job_applicant_doc.applicant_interview_round:
            if interview_round.interview_round == doc.interview_round:
                # Update the interview reference and status on creation or update
                interview_round.interview_reference = doc.name
                interview_round.interview_status = doc.status

                job_applicant_doc.save(ignore_permissions=True)
                break

def mark_interview_completed(doc, method):
    '''
    Mark the interview as completed in the Applicant Interview Round child table in Job Applicant upon submission of Interview.
    '''
    if doc.job_applicant and doc.interview_round:
        job_applicant_doc = frappe.get_doc("Job Applicant", doc.job_applicant)

        # Find the corresponding interview round in the Job Applicant's applicant_interview_round table
        for interview_round in job_applicant_doc.applicant_interview_round:
            if interview_round.interview_round == doc.interview_round:
                # Mark the interview as completed upon submission
                interview_round.interview_completed = 1

                job_applicant_doc.save(ignore_permissions=True)
                break

        all_interviews_completed = True
        for interview_round in job_applicant_doc.applicant_interview_round:
            if not interview_round.interview_completed:
                all_interviews_completed = False
                break

        # If all interviews are completed, set the Job Applicant status to 'Interview Completed'
        if all_interviews_completed:
            job_applicant_doc.status = "Interview Completed"

        job_applicant_doc.save(ignore_permissions=True)
