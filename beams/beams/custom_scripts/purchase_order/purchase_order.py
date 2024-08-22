
import frappe
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

@frappe.whitelist()
def create_todo_on_finance_verification(doc, method):
    """
        Create a ToDo for the CEO when a Purchase Order is either approved or rejected by Finance.
    """
    ceo_users = get_users_with_role("CEO")

    if not ceo_users:
        return

    if doc.workflow_state == "Approved by Finance":
        description = f"Approved by Finance: Purchase Order-{doc.supplier}.<br>Please proceed with the next step."
    elif doc.workflow_state == "Rejected By Finance":
        description = f"Rejected by Finance: Purchase Order-{doc.supplier}.<br>Please review and revise, or proceed with their feedback."
    else:
        return

    if not frappe.db.exists('ToDo', {
        'reference_name': doc.name,
        'reference_type': 'Purchase Order',
        'description': description
    }):
        add_assign({
            "assign_to": ceo_users,
            "doctype": "Purchase Order",
            "name": doc.name,
            "description": description
        })

def create_todo_on_purchase_order_creation(doc, method):
    """
        Create a ToDo for  Accounts User when a new Purchase Order is created.
    """
    users = get_users_with_role("Accounts User")

    if users:
        description = f"New Purchase Order Created: {doc.supplier}.<br>Please review and update details or take necessary actions."
        add_assign({
            "assign_to": users,
            "doctype": "Purchase Order",
            "name": doc.name,
            "description": description
        })
