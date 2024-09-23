
import frappe
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

@frappe.whitelist()
def create_todo_on_contract_creation(doc, method):
    """
    Create a ToDo for Accounts Manager when a new Contract is created.
    """
    users = get_users_with_role("Accounts Manager")
    if users:
        description = f"New Contract Created for {doc.party_name}.<br>Please review and update details or take necessary actions."
        add_assign({
            "assign_to": users,
            "doctype": "Contract",
            "name": doc.name,
            "description": description
        })

@frappe.whitelist()
def create_todo_on_contract_verified_by_finance(doc,method):
    """
    Creates a ToDo task for the CEO based on the workflow state of the Contract.
    - If the state is "Verified By Finance", creates a task for the CEO to proceed with the next step.
    - If the state is "Rejected By Finance", creates a task for the CEO to review and revise or proceed with feedback.
    """
    if doc.workflow_state == "Verified By Finance":
        ceo_users = get_users_with_role("CEO")
        if ceo_users:
            description = f"Verified  By Finance for Contract {doc.party_name}. Please Proceed with the Next Step."
            if not frappe.db.exists('ToDo', {'reference_name': doc.name, 'reference_type': 'Contract', 'description':description}):
                add_assign({
                    "assign_to": ceo_users,
                    "doctype": "Contract",
                    "name": doc.name,
                    "description": description
                })
    elif doc.workflow_state == "Rejected By Finance":
        ceo_users = get_users_with_role("CEO")
        if ceo_users:
            description = f"Rejected By Finance for Contract {doc.party_name}. Please Review and Revise, or Proceed with their Feedback."
            if not frappe.db.exists('ToDo', {'reference_name': doc.name, 'reference_type': 'Contract', 'description':description}):
                add_assign({
                    "assign_to": ceo_users,
                    "doctype": "Contract",
                    "name": doc.name,
                    "description": description
                })
