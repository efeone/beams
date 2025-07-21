# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeCheckinPermission(Document):
	pass


@frappe.whitelist()
def get_employee_for_current_user():
    """Fetches the Employee name linked to the currently logged-in user."""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    return employee


@frappe.whitelist()
def get_shift_for_employee_on_date(employee, date):
    """
    Returns the assigned shift for the employee on the given date
    if there is a Shift Assignment. Returns None if no assignment is found.
    """
    shift = frappe.db.get_value(
        "Shift Assignment",
        {
            "employee": employee,
            "status": "Active",
            "start_date": ["<=", date],
            "end_date": [">=", date]
        },
        "shift_type"
    )
    if not shift:
         shift = frappe.db.get_value("Employee",employee,"default_shift")
    return shift