import frappe

@frappe.whitelist()
def get_open_training_requests():
    return frappe.get_all(
        "Training Request",
        filters={"status": "Open"},
        fields=["name", "employee", "employee_name"]
    )
