import frappe
from frappe import _

def after_insert(doc, method):
    '''
        Method which triggers on after insert of Interview Feedback
    '''
    on_interview_feedback_creation(doc)


def validate(doc, method):
    '''
        Method which triggers on validate of Interview Feedback
    '''
    for row in doc.skill_assessment:
        rating = 0
        if row.score:
            if row.score > 10 or row.score < 0:
                frappe.throw(_("Score for skill {0} must be a number between 0 and 10.").format(frappe.bold(row.skill)))
            rating = float(row.score) / 10
        row.rating = rating

    for row in doc.interview_question_result:
        rating = 0
        if row.score:
            if row.score > 10 or row.score < 0:
                frappe.throw(_("Score for question {0} must be a number between 0 and 10.").format(frappe.bold(row.question)))
            rating = float(row.score) / 10
        row.rating = rating

def on_interview_feedback_creation(doc):
    '''
        Update the Job Applicant's status to 'Interview Ongoing'
    '''
    if frappe.db.exists('Job Applicant', doc.job_applicant):
        current_status = frappe.db.get_value('Job Applicant', doc.job_applicant, 'status')
        if current_status != 'Interview Ongoing':
            frappe.db.set_value('Job Applicant', doc.job_applicant, 'status', 'Interview Ongoing')

def on_submit(doc, method):
	'''
		On submission of an Interview Feedback document,
		append the feedback details to the corresponding Interview record
	'''
	interview_doc = frappe.get_doc('Interview', doc.interview)
	existing_interviewers = [d.interviewer for d in interview_doc.interview_feedback_details]

	if doc.interviewer not in existing_interviewers:
		interview_doc.append('interview_feedback_details', {
			'interviewer': doc.interviewer,
			'result': doc.result,
			'interview_feedback_reference': doc.name,
			'remarks': doc.feedback
		})
		interview_doc.save(ignore_permissions=True)

@frappe.whitelist()
def get_interview_details(interview_round):
    '''
        Fetch Questions and Skills
    '''
    # Fetch questions
    questions = frappe.get_all(
        'Interview Questions',
        filters={'parent': interview_round},
        fields=['question', 'answer', 'weight']
    )

    # Fetch expected skill set for skill assessment
    skill_assessment = frappe.get_all(
        'Expected Skill Set',
        filters={'parent': interview_round},
        fields=['skill', 'weight']
    )

    return {
        "questions": questions,
        "skill_assessment": skill_assessment
    }

def update_applicant_interview_round_from_feedback(doc, method):
    """
    Updates the interview round rating in the child table of Job Applicant
    and recalculates the overall applicant rating.
    """

    if not doc.job_applicant or not doc.interview_round:
        frappe.msgprint("Missing Job Applicant or Interview Round.")
        return

    if not frappe.db.exists("Job Applicant", doc.job_applicant):
        frappe.msgprint(f"Job Applicant {doc.job_applicant} does not exist.")
        return

    # Get the latest rating from Interview Feedback
    latest_rating = frappe.db.get_value("Interview", doc.interview, "average_rating")
    if latest_rating is None:
        frappe.msgprint("No Average Rating found.")
        return

    job_applicant = frappe.get_doc("Job Applicant", doc.job_applicant)

    for round in job_applicant.applicant_interview_rounds:
        if round.interview_round.strip() == doc.interview_round.strip():
            round.applicant_rating = float(latest_rating)
            break

    # Calculate the new overall rating
    ratings = [r.applicant_rating for r in job_applicant.applicant_interview_rounds if r.applicant_rating]
    job_applicant.applicant_rating = sum(ratings) / len(ratings) if ratings else 0

    job_applicant.save(ignore_permissions=True)

@frappe.whitelist()
def update_final_score(doc, method):
    '''
       Set final score from rating to interview  
    '''
    interview_id = doc.interview
    if not interview_id:
        return

    feedbacks = frappe.get_all(
        "Interview Feedback",
        filters={"interview": interview_id, "docstatus": 1},
        fields=["average_rating"]
    )


    # Extract ratings, ignoring None values
    ratings = [fb.average_rating for fb in feedbacks if fb.average_rating is not None]

    if ratings:
        # Calculate average and scale it to 10 (by multiplying by 2)
        avg_rating = sum(ratings) / len(ratings)
        average_final_score = round(avg_rating * 10, 2)  # Convert to 10 scale
        # Update the Interview doc field
        frappe.db.set_value("Interview", interview_id, "average_final_score", average_final_score)
    else:
        # No ratings found, set score to 0
        frappe.db.set_value("Interview", interview_id, "average_final_score", 0)
