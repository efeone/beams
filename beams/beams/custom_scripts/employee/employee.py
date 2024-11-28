import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, nowdate

@frappe.whitelist()
def create_event(employee_id=None, hod_user=None, target_doc=None):
    """
    Create an Event document mapped from an Employee record, adding both the Employee and the HOD
    as participants in the Event.
    """
    user = frappe.session.user
    if not employee_id:
        employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    hod_user = hod_user or user
    hod_employee_id = frappe.get_value("Employee", {"user_id": hod_user}, "name")
    doc = get_mapped_doc("Employee", employee_id, {
        "Employee": {
            "doctype": "Event"
        }
    }, target_doc)
    employee_participant = doc.append("event_participants", {})
    employee_participant.reference_docname = employee_id
    employee_participant.reference_doctype = "Employee"
    hod_participant = doc.append("event_participants", {})
    hod_participant.reference_docname = hod_employee_id
    hod_participant.reference_doctype = "Employee"

    return doc

@frappe.whitelist()
def get_employee_name_for_user(user_id):
    '''
    Fetch the Employee name associated with the given user_id.
    '''
    employee_name = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    return employee_name

@frappe.whitelist()
def after_insert_employee(doc, method):
    """
    Triggered after an Employee record is created.
    Fetches the default leave policy and leave period from Beams HR Settings,
    validates the configurations, and creates & submits a Leave Policy Assignment.
    """
    # Fetch default leave policy and leave period from Beams HR Settings
    leave_policy = frappe.db.get_single_value('Beams HR Settings', 'default_leave_policy')
    leave_period = frappe.db.get_single_value('Beams HR Settings', 'leave_period')

    if not leave_policy or not leave_period:
        return

    # Fetch leave period details
    leave_period_details = frappe.db.get_value(
        'Leave Period',
        leave_period,
        ['from_date', 'to_date'],
        as_dict=True
    )

    # Skip if leave period details are missing
    if not leave_period_details:
        return

    if not doc.name:
        return

    # Create Leave Policy Assignment
    leave_policy_assignment = frappe.get_doc({
        'doctype': 'Leave Policy Assignment',
        'employee': doc.name,
        'leave_policy': leave_policy,
        'leave_period': leave_period,
        'assignment_based_on': 'Leave Period',
        'effective_from': leave_period_details['from_date'],
        'effective_to': leave_period_details['to_date'],
    })

    # Save and submit the leave policy assignment
    leave_policy_assignment.insert()
    leave_policy_assignment.submit()
