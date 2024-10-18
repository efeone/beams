import frappe
from frappe import _
from frappe.model.document import Document

def validate(doc, method):
    if doc.cost_center:
        # Check if the cost center is already used in another department
        departments = frappe.get_list('Department', filters={'cost_center': doc.cost_center}, fields=['name'])

        if departments:
            department_name = departments[0].get('name')
            frappe.throw(
                _("The selected Cost Center is already assigned to Department: {0}. Please choose a different one.").format(department_name)
            )

@frappe.whitelist()
def get_hod_users(department_name):
    """
    Fetches the user IDs of employees who belong to a specific department and have the 'Hod' role.
    Returns a list of user IDs for filtering in the client-side code.
    """
    users = frappe.db.sql("""
        SELECT emp.user_id
        FROM `tabEmployee` emp
        JOIN `tabUser` usr ON usr.name = emp.user_id
        JOIN `tabHas Role` role ON role.parent = usr.name
        WHERE emp.department = %s AND role.role = 'Hod'
    """, (department_name,))

    return [user[0] for user in users]  # Return a list of user IDs
