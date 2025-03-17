import frappe

def execute():
    print("Patch to update INR data in Budget")
    for budget in frappe.db.get_all("Budget", pluck="name"):
        try:
            frappe.get_doc("Budget", budget).save()
        except Exception as e:
            frappe.log_error("Error while updating Budget for INR via patch", e, "Budget", budget)
