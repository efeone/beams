import frappe

def on_interview_feedback_creation(doc, method):
    '''
    Update the Job Applicant's status to 'Interview Ongoing' when an Interview Feedback is created.
    '''
    if frappe.db.exists("Job Applicant", doc.job_applicant):
        job_applicant_doc = frappe.get_doc("Job Applicant", doc.job_applicant)
        if job_applicant_doc.status != "Interview Ongoing":
            job_applicant_doc.status = "Interview Ongoing"
            job_applicant_doc.save()

@frappe.whitelist()
def fetch_details_from_interview_round(interview_round):
    '''
    Fetches skills and questions from the specified Interview Round.
    '''
    if not interview_round:
        frappe.throw("Please select a valid Interview Round.")

    if not frappe.db.exists("Interview Round", interview_round):
        frappe.throw(f"Interview Round '{interview_round}' does not exist.")    

    interview_round_doc = frappe.get_doc("Interview Round", interview_round)

    skills = []
    if interview_round_doc.expected_skill_set:
        for skill in interview_round_doc.expected_skill_set:
            skills.append({
                "skill": skill.skill,
                "weight": skill.weight
            })
    else:
        frappe.msgprint('No skills found in the selected Interview Round')

    questions = []
    if interview_round_doc.expected_question_set:
        for question in interview_round_doc.expected_question_set:
            questions.append({
                "question": question.question,
                "weight": question.weight
            })
    else:
        frappe.msgprint('No questions found in the selected Interview Round')

    return {
        "skills": skills,
        "questions": questions
    }
