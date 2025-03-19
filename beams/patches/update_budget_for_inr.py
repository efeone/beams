import frappe

def execute():
    print("Patch to update INR data in Budget")
    for budget in frappe.db.get_all("Budget", pluck="name"):
        try:
            doc = frappe.get_doc("Budget", budget)
            doc.budget_accounts_custom = []
            for row in doc.accounts:
                budget_row = row.as_dict()
                budget_row.pop('name')
                budget_row.pop('parentfield')
                doc.append('budget_accounts_custom', budget_row)
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error("Error while updating Budget for INR via patch", e, "Budget", budget)
