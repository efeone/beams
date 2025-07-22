import frappe
from frappe.desk.form.assign_to import add as add_assign

@frappe.whitelist()
def create_exit_clearance(doc, method=None):
    '''
    Create Employee Exit Clearance records and assign tasks for department heads.
    '''
    for row in doc.employee_clearance:
        department = row.department
        if not department :
            continue
        duplicates = [
            r for r in doc.employee_clearance
            if r.department == department and r.name != row.name
        ]
        if duplicates:
            frappe.throw(f"Department '{department}' is already selected in another row.")
        if row.employee_exit_clearance:
            continue
        existing_clearance = frappe.db.exists("Employee Exit Clearance", {
            "employee": doc.employee,
            "department": department
        })
        if existing_clearance:
            row.employee_exit_clearance = existing_clearance
            row.status = "Pending"
            continue
        department_head = frappe.db.get_value("Department", department, "head_of_department")
        department_head_user = frappe.db.get_value("Employee", department_head, "user_id") if department_head else None
        clearance = frappe.get_doc({
            "doctype": "Employee Exit Clearance",
            "employee": doc.employee,
            "department": department,
            "status": "Pending",
            "assigned_to": department_head_user or ""
        })
        clearance.insert(ignore_permissions=True)

        boarding_begins_on = frappe.db.get_value("Employee Separation", doc.name, "boarding_begins_on")
        if boarding_begins_on:
            clearance.db_set("employee_separation_begins_on", boarding_begins_on)

        if department_head_user:
            add_assign({
                "assign_to": [department_head_user],
                "doctype": "Employee Exit Clearance",
                "name": clearance.name,
                "description": f"Please review and complete the exit clearance for {doc.employee} in {department}."
            })
        row.employee_exit_clearance = clearance.name
        row.status = "Pending"