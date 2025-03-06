import frappe

def execute():
    employees = frappe.get_all("Employee", fields=["name", "no_of_children"])

    for emp in employees:
        no_of_children = 0
        if emp.no_of_children:
            try:
                no_of_children = int(emp.no_of_children)
            except ValueError:
                frappe.log_error(f"Invalid data for Employee {emp.name}: {emp.no_of_children}", "Data Conversion Error")
        frappe.db.set_value("Employee", emp.name, "no_of_children", no_of_children, update_modified=False)
    frappe.db.commit()
