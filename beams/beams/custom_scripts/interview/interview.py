import json
import frappe
from frappe import _
from six import string_types
from frappe.utils import get_link_to_form
from hrms.hr.doctype.interview.interview import Interview

class InterviewOverride(Interview):
    def on_submit(self):
        if self.status not in ["Cleared", "Rejected"]:
              frappe.throw(_("Only Interviews with Cleared or Rejected status can be submitted."),
                           title=_("Not Allowed"),
                           )

        # Fetch all interviewers from the Interview Details child table
        interviewers = [d.interviewer for d in self.interview_details if d.interviewer]

        # Fetch all submitted feedback records for this interview
        submitted_feedback = frappe.get_all(
            "Interview Feedback",
            filters={"interview": self.name, "docstatus": 1},
            fields=["interviewer"],
        )

        # Extract interviewers who have submitted feedback
        submitted_interviewers = {feedback["interviewer"] for feedback in submitted_feedback}

        # Identify interviewers who haven't submitted feedback
        missing_feedback = [i for i in interviewers if i not in submitted_interviewers]

        if missing_feedback:
            frappe.throw(
                _("Interview cannot be submitted. The following interviewers have not submitted feedback: {0}")
                .format(", ".join(missing_feedback)),
                title=_("Pending Feedback"),
            )


@frappe.whitelist()
def get_interview_skill_and_question_set(interview_round, interviewer=False, interview_name=False):
	'''
        Method to get Interview Skills and Questions from Interview Round or existing Interview Feedback
	'''
	feedback_exists = False
	if interviewer and interview_name:
		feedback_exists = frappe.db.exists(
			"Interview Feedback",
			{"interviewer": interviewer, "interview": interview_name, "docstatus": 0},
		)
	if feedback_exists:
		interview_feedback = frappe.get_doc('Interview Feedback', feedback_exists)
		return interview_feedback.interview_question_result, interview_feedback.skill_assessment, feedback_exists
	else:
		question = frappe.get_all('Interview Questions', filters ={'parent': interview_round}, fields=['question', 'answer', 'weight'])
		skill = frappe.get_all('Expected Skill Set', filters ={'parent': interview_round}, fields=['skill'])
		return question, skill, False

@frappe.whitelist()
def create_interview_feedback(data, interview_name, interviewer, job_applicant, method='save', feedback_exists=False):
	'''
	    Method to create Interview Feedback
	'''
	if isinstance(data, string_types):
		data = frappe._dict(json.loads(data))

	if frappe.session.user != interviewer:
		frappe.throw(_('Only Interviewer Are allowed to submit Interview Feedback'))

	interview_feedback = False

	if feedback_exists:
		interview_feedback = frappe.get_doc('Interview Feedback', feedback_exists)
	else:
		interview_feedback = frappe.new_doc('Interview Feedback')
		interview_feedback.interview = interview_name
		interview_feedback.interviewer = interviewer
		interview_feedback.job_applicant = job_applicant

	if interview_feedback:
		for d in data.skill_set:
			d = frappe._dict(d)
			if not d.parent:
				interview_feedback.append('skill_assessment', {'skill': d.skill, 'score': d.score})
			else:
				for skill in interview_feedback.skill_assessment:
					if skill.name == d.name:
						skill.score = d.score

		if data.questions:
			for dq in data.questions:
				dq = frappe._dict(dq)
				if not dq.parent:
					interview_feedback.append('interview_question_result', {'question': dq.question, 'answer': dq.answer,
						'weight': dq.weight, 'applicant_answer': dq.applicant_answer, 'score': dq.score})
				else:
					for question in interview_feedback.interview_question_result:
						if question.name == dq.name:
							question.applicant_answer = dq.applicant_answer
							question.score = dq.score

		interview_feedback.result = data.result
		interview_feedback.feedback = data.feedback
		if method == 'save':
			interview_feedback.flags.ignore_mandatory=True
		interview_feedback.save()
		if method == 'submit':
			interview_feedback.submit()

		frappe.msgprint(_('{1} Interview Feedback {0} successfully!').format(
		get_link_to_form('Interview Feedback', interview_feedback.name), method.title()))

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

        # Find the corresponding interview round in the Job Applicant's applicant_interview_rounds table
        for interview_round in job_applicant_doc.applicant_interview_rounds:
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
        if frappe.db.exists("Job Applicant", doc.job_applicant):
            job_applicant_doc = frappe.get_doc("Job Applicant", doc.job_applicant)

            # Find the corresponding interview round in the Job Applicant's applicant_interview_rounds table
            for interview_round in job_applicant_doc.applicant_interview_rounds:
                if interview_round.interview_round == doc.interview_round:
                    # Mark the interview as completed upon submission
                    interview_round.interview_completed = 1

                    job_applicant_doc.save(ignore_permissions=True)
                    break

            all_interviews_completed = True
            for interview_round in job_applicant_doc.applicant_interview_rounds:
                if not interview_round.interview_completed:
                    all_interviews_completed = False
                    break

            # If all interviews are completed, set the Job Applicant status to 'Interview Completed'
            if all_interviews_completed:
                job_applicant_doc.status = "Interview Completed"

            job_applicant_doc.save(ignore_permissions=True)

@frappe.whitelist()
def update_job_applicant_status(doc, method=None):
    job_applicant = doc.job_applicant

    # Get the job opening linked to the interview
    job_opening = doc.job_opening
    if not job_opening:
        return

    # Get the job requisition from job opening
    job_requisition = frappe.db.get_value("Job Opening", job_opening, "job_requisition")
    if not job_requisition:
        return

    # Get required interview rounds from job requisition
    required_rounds = frappe.get_all(
        "Interview Rounds",
        filters={"parent": job_requisition},
        pluck="interview_round"
    )

    # Get completed interview rounds from applicant
    completed_rounds = frappe.get_all(
        "Interview",
        filters={
            "job_applicant": job_applicant,
            "status": ["in", ["Cleared", "Rejected"]],
            "interview_round": ["is", "set"]
        },
        pluck="interview_round"
    )

    # Compare sets
    if set(required_rounds).issubset(set(completed_rounds)):
        frappe.db.set_value("Job Applicant", job_applicant, "status", "Interview Completed")
    else:
        frappe.db.set_value("Job Applicant", job_applicant, "status", "Interview Ongoing")

@frappe.whitelist()
def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Allow Administrator to see all interviews
    if "System Manager" in user_roles:
        return None

    # Restrict Interviewers to see only scheduled interviews where they are assigned
    if "Interviewer" in user_roles:
        conditions = """
            EXISTS (
                SELECT 1 FROM `tabInterview Detail` id
                WHERE id.parent = `tabInterview`.name
                AND id.interviewer = '{user}'
            )
        """.format(user=user)
        return conditions

    return None


def update_applicant_interview_rounds(doc, method):
    """
    Update the Job Applicant's applicant_interview_rounds table when a new Interview is created.
    """
    if not doc.job_applicant:
        return

    job_applicant = frappe.get_doc("Job Applicant", doc.job_applicant)
    existing_rounds = {row.interview_round for row in job_applicant.applicant_interview_rounds}

    if doc.interview_round in existing_rounds:
        return

    job_applicant.append("applicant_interview_rounds", {
        "interview_round": doc.interview_round,
        "interview_status": doc.status
    })

    job_applicant.save(ignore_permissions=True)

@frappe.whitelist()
def get_job_applicant_dashboard_html(job_applicant):
    if not job_applicant:
        return {"html": "<p>No Job Applicant selected.</p>"}

    doc = frappe.get_doc("Job Applicant", job_applicant)

    html = frappe.render_template(
        "beams/beams/custom_scripts/interview/interview_dashboard.html",
        {"job_applicant": doc}
    )

    return {"html": html}
