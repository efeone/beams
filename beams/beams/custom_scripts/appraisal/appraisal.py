import frappe

@frappe.whitelist()
def get_appraisal_summary(appraisal_template, employee_feedback=None):
    '''
        This function generates an appraisal summary in the form of an HTML table.
    '''
    if not frappe.db.exists("Appraisal Template", appraisal_template):
        return "Appraisal Template does not exist."

    template_doc = frappe.get_doc("Appraisal Template", appraisal_template)
    if employee_feedback and frappe.db.exists("Employee Performance Feedback", employee_feedback):
        feedback_doc = frappe.get_doc("Employee Performance Feedback", employee_feedback)

    key_results = []
    total_marks = 0

    for row in template_doc.rating_criteria:
        marks = ""
        if feedback_doc:
            for feedback_row in feedback_doc.feedback_ratings:
                if feedback_row.criteria == row.criteria:
                    marks = feedback_row.marks
                    break
        if marks:
            total_marks += float(marks)
        key_results.append({"key_result": row.criteria, "marks": marks})

    label_for_department_kra = template_doc.label_for_department_kra or "Quality and Development Assessment"
    label_for_company_kra = template_doc.label_for_company_kra or "Alignment with Core Values"

    department_marks = feedback_doc.department_average_score if feedback_doc else ""
    company_marks = feedback_doc.company_average_score if feedback_doc else ""

    if template_doc.department_rating_criteria:
        key_results.append({"key_result": label_for_department_kra, "marks": department_marks})
        if department_marks:
            total_marks += float(department_marks)

    if template_doc.company_rating_criteria:
        key_results.append({"key_result": label_for_company_kra, "marks": company_marks})
        if company_marks:
            total_marks += float(company_marks)

    total_criteria = len([result for result in key_results if result.get('marks')])
    final_average_score = total_marks / total_criteria if total_criteria > 0 else 0

    # Generate the HTML table
    table_html = """
        <table class="table table-bordered" style="width:100%;">
            <thead>
                <tr>
                    <th style="width: 10%;">Serial No</th>
                    <th>Key Results</th>
                    <th style="width: 20%;"><center>Marks by AO</center></th>
                </tr>
            </thead>
            <tbody>
    """

    # Add rows to the table
    for idx, row in enumerate(key_results, start=1):
        table_html += f"""
            <tr>
                <td><center>{idx}</center></td>
                <td>{row.get('key_result')}</td>
                <td><center>{row.get('marks', '')}</center></td>
            </tr>
        """

    # Add final rows for Total Marks and Final Average Score
    table_html += f"""
        <tr>
            <td colspan="2" style="text-align: right;"><b>Total Marks</b></td>
            <td><b><center>{total_marks:.2f}</center></b></td>
        </tr>
        <tr>
            <td colspan="2" style="text-align: right;"><b>Final Average Score</b><br><br>(on 5 : total of scores for KRAs 1 to 10 divided by 10)</td>
            <td><b><center>{final_average_score:.2f}</center></b></td>
        </tr>
    """

    table_html += "</tbody></table>"

    return table_html

@frappe.whitelist()
def get_feedback_for_appraisal(appraisal_name):
    if not frappe.db.exists("Appraisal", appraisal_name):
        return "Appraisal does not exist."
    feedback_name = frappe.db.get_value("Employee Performance Feedback",{"appraisal": appraisal_name},"name")
    return feedback_name

@frappe.whitelist()
def map_appraisal_to_event(source_name):
    """
    Map fields from Appraisal to a new Event.
    """
    source_doc = frappe.get_doc("Appraisal", source_name)

    # Create a new Event document
    event_doc = frappe.new_doc("Event")

    # Add participants
    event_doc.append("event_participants", {
        "reference_doctype": "Employee",
        "reference_docname": source_doc.employee
    })

    # Optionally, add the logged-in user as a participant
    user_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if user_employee:
        # If the logged-in user has an Employee ID, add them as a participant
        event_doc.append("event_participants", {
            "reference_doctype": "Employee",
            "reference_docname": user_employee
        })
    else:
        # If the logged-in user doesn't have an Employee ID, use their User ID
        event_doc.append("event_participants", {
            "reference_doctype": "User",
            "reference_docname": frappe.session.user
        })

    return event_doc
