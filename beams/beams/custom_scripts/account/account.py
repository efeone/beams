import frappe
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

def create_todo_on_creation(doc, method, doctype_name, action_description):
    users = get_users_with_role("Accounts User")

    if users:
        description = f"New {doctype_name} Created: {doc.name}.<br>{action_description}"

        add_assign({
            "assign_to": users,
            "doctype": doctype_name,
            "name": doc.name,
            "description": description
        })

def create_todo_on_creation_for_account(doc, method):
    create_todo_on_creation(doc, method, "Account", "Please review and update details or take necessary actions.")

def create_todo_on_creation_for_customer(doc, method):
    create_todo_on_creation(doc, method, "Customer", "Please review and update details or take necessary actions.")

def create_todo_on_creation_for_supplier(doc, method):
    create_todo_on_creation(doc, method, "Supplier", "Please review and update details or take necessary actions.")
