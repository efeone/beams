import frappe
from frappe import _
from frappe.model.document import Document

@frappe.whitelist()
def get_hod_users(department_name):
    """
    Fetches the user IDs of employees who belong to a specific department and have the 'HOD' role.
    Returns a list of user IDs for filtering in the client-side code.
    """
    users = frappe.db.sql("""
        SELECT emp.user_id
        FROM `tabEmployee` emp
        JOIN `tabUser` usr ON usr.name = emp.user_id
        JOIN `tabHas Role` role1 ON role1.parent = usr.name AND role1.role = 'HOD'
        JOIN `tabHas Role` role2 ON role2.parent = usr.name AND role2.role = 'Employee'
        WHERE emp.department = %s
    """, (department_name,))

    return [user[0] for user in users]  # Return a list of user IDs
