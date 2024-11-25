import frappe


def validate(doc ,method):
    employee_gender = frappe.db.get_value("Employee", doc.employee, "gender")
    if not employee_gender:
        frappe.throw(f"Gender not found for Employee {doc.employee}. Please ensure gender is set in the Employee record.")

    is_valid_mapping = frappe.db.exists(
        "Gender Leave Type Mapping",
        {
            "leave_type": doc.leave_type,
            "gender": employee_gender,
        }
    )

    if not is_valid_mapping:
        frappe.throw(f"The Selected Leave Type is not permitted for the {doc.employee}")  