import frappe
import json
from frappe import _
from six import string_types
from frappe.utils import get_link_to_form
import datetime
from frappe.desk.form.assign_to import add as add_assign


def validate_kra_marks(doc, method):
    fields = ['employee_self_kra_rating', 'dept_self_kra_rating', 'company_self_kra_rating']

    for field in fields:
        if doc.get(field):  # Check if the child table has data
            for row in doc.get(field):
                if row.marks and float(row.marks) > 5:
                    frappe.throw(_("Marks cannot be greater than 5."))

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

    # Save the document
    feedback_doc.flags.ignore_mandatory = True  # Allow ignoring mandatory fields
    feedback_doc.save()

    # Submit the document
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
    feedback_doc = None

    feedback_exists = employee_feedback and frappe.db.exists("Employee Performance Feedback", employee_feedback)
    if feedback_exists:
        feedback_doc = frappe.get_doc("Employee Performance Feedback", employee_feedback)

    key_results = []
    total_marks = 0
    total_criteria_count = 0

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
    total_criteria_count = len(key_results)
    final_average_score = round(total_marks / total_criteria if total_criteria > 0 else 0, 3)

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
            <td colspan="2" style="text-align: right;"><b>Final Average Score</b><br><br>(on 5 : total of scores for KRAs 1 to {total_criteria_count} divided by {total_criteria_count})</td>
            <td><b><center>{final_average_score:.2f}</center></b></td>
        </tr>
    """

    table_html += "</tbody></table>"

    return table_html, final_average_score

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
    categories = frappe.get_all('Appraisal Category', fields=['category', 'category_description'])
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
    try:
        # Fetch the Appraisal document
        source_doc = frappe.get_doc("Appraisal", source_name)

        # Create a new Event document
        event_doc = frappe.new_doc("Event")
        event_doc.appraisal_reference = source_doc.name
        event_doc.subject = "Appraisal Event for {}".format(source_doc.employee)
        event_doc.starts_on = datetime.datetime.now()

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

    except Exception as e:
        # Log the error and raise it
        frappe.log_error(message=str(e), title="Error in mapping Appraisal to Event")
        raise frappe.exceptions.ValidationError(f"Error: {str(e)}")

@frappe.whitelist()
def check_existing_event(appraisal_reference):
    """
    Check if an Event exists for the given Appraisal.

    """
    event = frappe.db.get_value("Event", {"appraisal_reference": appraisal_reference}, "name")
    return event if event else None

@frappe.whitelist()
def assign_tasks_sequentially(doc):
    """
    Sends an email notification to the assessment officer to review the appraisal.
    """
    appraisal = frappe.get_doc("Appraisal", doc)
    assessment_officer_id = frappe.db.get_value("Employee", appraisal.employee, "assessment_officer")

    if not assessment_officer_id:
        frappe.throw(f"Assessment Officer not set for employee {appraisal.employee}")

    user_id, officer_name = frappe.db.get_value("Employee", assessment_officer_id, ["user_id", "employee_name"])

    if not user_id:
        frappe.throw(f"No User ID found for assessment officer {assessment_officer_id}")

    # Get email template
    template_name = frappe.db.get_single_value("Beams HR Settings", "assessment_reminder_template")
    if not template_name:
        frappe.throw("Please set 'Assessment Reminder Template' in Beams HR Settings.")

    template = frappe.get_doc("Email Template", template_name)

    context = {
        "doc": appraisal,
        "employee_name": appraisal.employee_name,
        "officer_name": officer_name,
    }
    subject = frappe.render_template(template.subject or '', context)
    message = frappe.render_template(template.response or template.message or '', context)
    
    frappe.sendmail(recipients=frappe.db.get_value("User", user_id, "email"), subject=subject, message=message)

    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": subject,
        "for_user": user_id,
        "type": "Alert",
        "document_type": "Appraisal",
        "document_name": appraisal,
        "from_user": frappe.session.user,
        "email_content": message
    }).insert(ignore_permissions=True)

    frappe.msgprint(f"Notification sent to {officer_name} for appraisal review.")
    return {"status": "ok"}

@frappe.whitelist()
def get_appraisal_template_criteria(appraisal_template_name):
    '''
        Fetch rating criteria details for a given Appraisal Template.
    '''
    if not frappe.db.exists('Appraisal Template', appraisal_template_name):
        return "Appraisal Template does not exist."
    template = frappe.get_doc('Appraisal Template', appraisal_template_name)
    employee_criteria = [
        {'criteria': row.criteria, 'per_weightage': row.per_weightage or 0}
        for row in (template.get('rating_criteria') or [])
    ]
    department_criteria = [
        {'criteria': row.criteria, 'per_weightage': row.per_weightage or 0}
        for row in (template.get('department_rating_criteria') or [])
    ]
    company_criteria = [
        {'criteria': row.criteria, 'per_weightage': row.per_weightage or 0}
        for row in (template.get("company_rating_criteria") or [])
    ]
    if not (employee_criteria or department_criteria or company_criteria):
        return {'success': False, 'message': _('No rating criteria found in the selected template.')}

    return {
        'success': True,
        'employee_criteria': employee_criteria,
        'department_criteria': department_criteria,
        'company_criteria': company_criteria,
    }

@frappe.whitelist()
def validate_appraisal(doc, method):
    '''
    Validate the Appraisal document and calculate totals and averages.
    '''
    employee_total, employee_average = calculate_total_and_average(doc, 'employee_self_kra_rating')
    doc.total_employee_self_kra_rating = employee_total
    doc.avg_employee_self_kra_rating = employee_average

    dept_total, dept_average = calculate_total_and_average(doc, 'dept_self_kra_rating')
    doc.total_dept_self_kra_rating = dept_total
    doc.avg_dept_self_kra_rating = dept_average

    company_total, company_average = calculate_total_and_average(doc, 'company_self_kra_rating')
    doc.total_company_self_kra_rating = company_total
    doc.avg_company_self_kra_rating = company_average

def calculate_total_and_average(doc, table):
    '''
    Function to calculate total and average
    '''
    total = 0
    count = 0
    rows = doc.get(table, [])
    if not rows:
        return total, 0  # No rows to calculate, return total 0 and average 0

    for row in rows:
        if row.marks:
            total += float(row.marks)
            count += 1
            row.rating = (float(row.marks) / 5)

    # Calculate average if count > 0
    average = total / count if count > 0 else 0
    return total, average

@frappe.whitelist()
def get_category_based_on_marks(final_average_score):
    '''
    This method will return the best applicable category based on the final average score from the appraisal.
    '''
    category = None
    filters = {
        'appraisal_threshold': ['<=', final_average_score]
    }

    # Fetch the categories based on threshold
    categories = frappe.db.get_all('Appraisal Category', filters=filters, order_by='appraisal_threshold desc', fields=['name', 'appraisal_threshold'])

    if categories:
        # Return the name of the first matching category
        category = categories[0].get('name')

    return category

@frappe.whitelist()
def set_category_based_on_marks(doc, method):
    '''
    Set the category_based_on_marks field in the Appraisal DocType based on the final_average_score.
    '''
    # Get the category based on final_average_score
    category = get_category_based_on_marks(doc.final_average_score)

    # Update the Appraisal document
    if category:
        doc.category_based_on_marks = category
