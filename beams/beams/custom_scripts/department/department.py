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

@frappe.whitelist()
def get_used_cost_centers():
    """
    Fetch departments that have a cost center set.
    Returns a list of used cost centers.
    """
    # Fetch departments with a cost center set
    departments = frappe.db.get_list(
        'Department',
        fields=['cost_center'],
        filters={'cost_center': ['is', 'set']}
    )

    # Extract the cost centers from the result
    used_cost_centers = [department['cost_center'] for department in departments]

    return used_cost_centers
