import frappe
import json
from frappe import _
from six import string_types
from frappe.utils import get_link_to_form

@frappe.whitelist()
def create_employee_feedback(data, employee , appraisal_name , feedback_exists=False, method='save'):
    '''
    Method to create or update Employee Performance Feedback.
    If feedback_exists is provided, it will update the existing feedback document.
    Otherwise, it creates a new one.
    '''
    # If the data is a string, convert it to a dictionary
    if isinstance(data, string_types):
        data = frappe._dict(json.loads(data))

    # Fetch the feedback document if it exists, otherwise create a new one
    if feedback_exists:
        feedback_doc = frappe.get_doc('Employee Performance Feedback', feedback_exists)
    else:
        feedback_doc = frappe.new_doc('Employee Performance Feedback')
        feedback_doc.employee = employee
        feedback_doc.appraisal = appraisal_name
        feedback_doc.reviewer = frappe.session.user  # Set reviewer as the current user
    # Append data to the child tables (employee, department, company feedback)
    if "employee_criteria" in data:
        for criterion in data["employee_criteria"]:
            feedback_doc.append('feedback_ratings', {
                'criteria': criterion.get("criteria"),
                'marks': criterion.get("marks"),
                'per_weightage':criterion.get("per_weightage")
            })

    if "department_criteria" in data:
        for criterion in data["department_criteria"]:
            feedback_doc.append('department_criteria', {
                'criteria': criterion.get("criteria"),
                'marks': criterion.get("marks"),
                'per_weightage':criterion.get("per_weightage")
            })

    if "company_criteria" in data:
        for criterion in data["company_criteria"]:
            feedback_doc.append('company_criteria', {
                'criteria': criterion.get("criteria"),
                'marks': criterion.get("marks"),
                'per_weightage':criterion.get("per_weightage")
            })

    # Add general feedback and result
    feedback_doc.feedback = data.get("feedback")
    feedback_doc.result = data.get("result")

    # Save or submit based on the method parameter
    if method == 'save':
        feedback_doc.flags.ignore_mandatory = True
        feedback_doc.save()
    elif method == 'submit':
        feedback_doc.submit()

    # Send a message to confirm the action
    frappe.msgprint(_('{1} Employee Performance Feedback {0} successfully!').format(
        get_link_to_form('Employee Performance Feedback', feedback_doc.name), method.title()))

    return feedback_doc.name  # Return the name of the created/updated feedback document


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
def get_categories_table():
    '''
         Fetches and sorts all categories from the Category doctype, then generates an HTML table displaying category names and descriptions.
    '''
    categories = frappe.get_all('Category', fields=['category', 'category_description'])
    categories.sort(key=lambda x: x['category'])

    categories_html = """
        <br><table border="1" style="width: 100%; text-align: center; border-collapse: collapse;">
            <thead>
                <tr>"""

    for category in categories:
        categories_html += f"<th>{category['category']}</th>"

    categories_html += "</tr></thead><tbody><tr>"

    for category in categories:
        categories_html += f"<td>{category['category_description']}</td>"

    categories_html += "</tr></tbody></table><br>"

    return categories_html

@frappe.whitelist()
def add_to_category_details(parent_docname, category, remarks, employee, designation):
    '''
        Adds a new row with category details (category, remarks, employee, designation) to the category_details child table of an Appraisal document and saves it.
    '''
    try:
        parent_doc = frappe.get_doc("Appraisal", parent_docname)
        child_row = parent_doc.append("category_details", {
            "category": category,
            "remarks": remarks,
            "employee": employee,
            "designation": designation
        })
        parent_doc.save()

        return "Success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Add to Category Details Error")
        return "Failed"

@frappe.whitelist()
def map_appraisal_to_event(source_name):
    '''
    Map fields from Appraisal to a new Event.
    '''
    source_doc = frappe.get_doc("Appraisal", source_name)

    # Create a new Event document
    event_doc = frappe.new_doc("Event")
    event_doc.appraisal_reference = source_doc.name
    event_doc.subject = "Appraisal Event for {}".format(source_doc.employee)
    event_doc.starts_on = frappe.utils.now_datetime()

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

    # Insert the Event document
    event_doc.insert()

    # Link the Event to the Appraisal
    if source_doc.docstatus == 1:  # Check if the Appraisal is submitted
        frappe.db.set_value("Appraisal", source_name, "event_reference", event_doc.name)
    else:
        source_doc.event_reference = event_doc.name
        source_doc.save()

    return event_doc
