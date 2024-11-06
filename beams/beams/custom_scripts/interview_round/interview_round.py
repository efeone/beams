import frappe

@frappe.whitelist()
def get_expected_question_set(interview_round):
    """
    Fetch the expected questions for the given interview round.
    """
    # Fetch the Interview Round document
    interview_round_doc = frappe.get_doc("Interview Round", interview_round)

    # Assuming 'expected_question_set' is the child table name in Interview Round DocType
    if interview_round_doc and interview_round_doc.expected_question_set:
        # Extract the expected questions
        expected_questions = [
            {
                'question': question.question  # Access the 'question' field from the child table
            }
            for question in interview_round_doc.expected_question_set
        ]
        return expected_questions  # Return the list of expected questions
    return []  # Return an empty list if no questions found
