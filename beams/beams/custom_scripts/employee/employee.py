import frappe
from frappe.model.mapper import get_mapped_doc

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
    """
    Fetch the Employee name associated with the given user_id.
    """
    employee_name = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    return employee_name
