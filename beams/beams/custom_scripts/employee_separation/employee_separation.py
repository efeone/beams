import frappe
from frappe.desk.form.assign_to import add as add_assign

@frappe.whitelist()
def create_exit_clearance(doc, method):
    '''
    Create Employee Exit Clearance records and assign tasks for department heads.
    '''

    for row in doc.employee_clearance:
        department = row.department
        status = row.status

        if status == "Completed":
            continue
        
        # Check if an Employee Exit Clearance already exists for this department
        existing_clearance = frappe.db.exists(
            "Employee Exit Clearance",
            {"employee": doc.employee, "department": department}
        )

        if existing_clearance:
            frappe.db.set_value(
                "Employee Clearance", 
                row.name, 
                "employee_exit_clearance", 
                existing_clearance
                )
            frappe.msgprint(f"Employee Exit Clearance already exists for <b>Employee</b>: {doc.employee} in <b>Department</b>: {department}.", title="Already Exists", indicator="blue")
            continue

        department_head = frappe.db.get_value("Department", department, "head_of_department")
        department_head_user = frappe.db.get_value("Employee", department_head, "user_id") if department_head else None
        
        # Create the Employee Exit Clearance document
        exit_clearance = frappe.get_doc({
            "doctype": "Employee Exit Clearance",
            "employee": doc.employee,
            "department": department,
            "status": "Pending",
            "assigned_to": department_head_user or ""
        })
        exit_clearance.insert(ignore_permissions=True)

        boarding_begins_on = frappe.db.get_value("Employee Separation", doc.name, "boarding_begins_on")
        if boarding_begins_on:
            frappe.db.set_value("Employee Exit Clearance", exit_clearance.name, "employee_separation_begins_on", boarding_begins_on)

        frappe.db.set_value("Employee Clearance", row.name, "employee_exit_clearance", exit_clearance.name)
        frappe.db.set_value("Employee Clearance", row.name, "status", "Pending")

        admin_message = f"Please review and complete the exit clearance process for Employee {doc.employee} in Department: {department}."

        if department_head_user:
            add_assign({
                "assign_to": [department_head_user],
                "doctype": "Employee Exit Clearance",
                "name": exit_clearance.name,
                "description": admin_message
            })
