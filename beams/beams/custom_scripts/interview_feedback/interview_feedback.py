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

def on_interview_feedback_creation(doc):
    '''
        Update the Job Applicant's status to 'Interview Ongoing'
    '''
    if frappe.db.exists('Job Applicant', doc.job_applicant):
        current_status = frappe.db.get_value('Job Applicant', doc.job_applicant, 'status')
        if current_status != 'Interview Ongoing':
            frappe.db.set_value('Job Applicant', doc.job_applicant, 'status', 'Interview Ongoing')

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
