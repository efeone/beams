
import frappe

@frappe.whitelist()
def get_expected_question_set(interview_round):
    """
    Fetch the expected questions for the given interview round.
    """
    # Fetch the Interview Round document
    interview_round_doc = frappe.get_doc("Interview Round", interview_round)

    # Assuming 'expected_questions' is the child table name in Interview Round Doctype
    if interview_round_doc and interview_round_doc.expected_question_set:
        # Return the list of expected questions
        return interview_round_doc.expected_question_set
    return []
