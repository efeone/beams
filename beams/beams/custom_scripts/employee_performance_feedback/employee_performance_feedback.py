import frappe

@frappe.whitelist()
def update_criteria(doc, method):
    # Update scores for employee, department, and company based on their respective child tables
    update_employee_criteria(doc, method)
    update_department_criteria(doc, method)
    update_company_criteria(doc, method)

def calculate_total_and_average(child_table):
    total_score = 0
    total_items = 0

    # Loop through the child table and sum the marks
    for row in child_table:
        total_score += row.marks
        total_items += 1

    # Calculate the average marks
    average_score = total_score / total_items if total_items > 0 else 0

    return total_score, average_score

@frappe.whitelist()
def update_employee_criteria(doc, method):
    # Calculate total and average marks for feedback_ratings
    total_score, average_score = calculate_total_and_average(doc.feedback_ratings)
    doc.employee_total_score = total_score
    doc.employee_average_score = average_score

@frappe.whitelist()
def update_department_criteria(doc, method):
    # Calculate total and average marks for department_criteria
    total_score, average_score = calculate_total_and_average(doc.department_criteria)
    doc.department_total_score = total_score
    doc.department_average_score = average_score

@frappe.whitelist()
def update_company_criteria(doc, method):
    # Calculate total and average marks for company_criteria
    total_score, average_score = calculate_total_and_average(doc.company_criteria)
    doc.company_total_score = total_score
    doc.company_average_score = average_score

def validate(doc, method):
    """
    Method which triggers on validate of Employee Performance Feedback.
    Ensures marks are between 0-5 and assigns them to the rating field in all child tables.
    """
    def validate_and_set_rating(child_table):
        """
        Helper function to validate marks and set them as ratings in a child table.
        """
        for row in child_table:
            if row.marks is not None:
                if row.marks < 0 or row.marks > 5:
                    frappe.throw(
                        _("Marks for criteria {0} must be a number between 0 and 5.").format(
                            frappe.bold(row.criteria)
                        )
                    )
                rating = (float(row.marks) / 10) * 2
            row.rating = rating
    # Validate and set ratings in all child tables
    validate_and_set_rating(doc.feedback_ratings)  # For employee criteria
    validate_and_set_rating(doc.department_criteria)  # For department criteria
    validate_and_set_rating(doc.company_criteria)  # For company criteria
