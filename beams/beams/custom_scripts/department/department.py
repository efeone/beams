import frappe
    """
    Fetches the user IDs of employees who belong to a specific department and have the 'Hod' role.
    Returns a list of user IDs for filtering in the client-side code.
    """
@frappe.whitelist()
def get_hod_users(department_name):
    users = frappe.db.sql("""
        SELECT emp.user_id
        FROM `tabEmployee` emp
        JOIN `tabUser` usr ON usr.name = emp.user_id
        JOIN `tabHas Role` role ON role.parent = usr.name
        WHERE emp.department = %s AND role.role = 'Hod'
    """, (department_name,))

    return [user[0] for user in users]  # Return a list of user IDs
