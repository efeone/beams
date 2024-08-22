import frappe
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

@frappe.whitelist()
def create_todo_on_finance_verification(doc, method):

        if doc.workflow_state == "Approved by Finance":
            ceo_users = get_users_with_role("CEO")
            if ceo_users:
                description = f"Approved by Finance: Purchase Order-{doc.supplier}.<br>Please proceed with the next step."
                if not frappe.db.exists('ToDo', {'reference_name': doc.name, 'reference_type': 'Purchase Order', 'description':description}):
                    add_assign({
                        "assign_to": ceo_users,
                        "doctype": "Purchase Order",
                        "name": doc.name,
                        "description": description
                    })
        elif doc.workflow_state == "Rejected By Finance":
            ceo_users = get_users_with_role("CEO")
            if ceo_users:
                description = f"Rejected by Finance: Purchase Order-{doc.supplier}.<br>Please review and revise, or proceed with their feedback."
                if not frappe.db.exists('ToDo', {'reference_name': doc.name, 'reference_type': 'Purchase Order', 'description':description}):
                    add_assign({
                        "assign_to": ceo_users,
                        "doctype": "Purchase Order",
                        "name": doc.name,
                        "description": description
                    })
