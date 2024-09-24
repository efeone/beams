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
def create_todo_on_contract_verified_by_finance(doc, method):
    """
    Creates a ToDo task for the CEO based on the workflow state of the Contract.
    - If the state is "Verified By Finance", creates a task for the CEO to proceed with the next step.
    - If the state is "Rejected By Finance", creates a task for the CEO to review and revise or proceed with feedback.
    """
    ceo_users = get_users_with_role("CEO")
    if doc.workflow_state == "Verified By Finance" and ceo_users:
        description = f"Verified By Finance for Contract {doc.party_name}. Please Proceed with the Next Step."
        if not frappe.db.exists('ToDo', {'reference_name': doc.name, 'reference_type': 'Contract', 'description': description}):
            add_assign({
                "assign_to": ceo_users,
                "doctype": "Contract",
                "name": doc.name,
                "description": description
            })

    elif doc.workflow_state == "Rejected By Finance" and ceo_users:
        description = f"Rejected By Finance for Contract {doc.party_name}. Please Review and Revise, or Proceed with their Feedback."
        if not frappe.db.exists('ToDo', {'reference_name': doc.name, 'reference_type': 'Contract', 'description': description}):
            add_assign({
                "assign_to": ceo_users,
                "doctype": "Contract",
                "name": doc.name,
                "description": description
            })

def on_submit(doc, method):
    """
    Check if a Purchase Invoice exists for the contract. If not, create one.
    """
    if doc.workflow_state == "Approved":
        # Check if a Purchase Invoice already exists for this contract and supplier
        existing_invoice = frappe.db.exists({
            "doctype": "Purchase Invoice",
            "supplier": doc.party_name,  # Using 'party_name' for Supplier
            "contract_reference": doc.name  # Add contract reference field to the Purchase Invoice
        })

        if existing_invoice:
            frappe.throw(f"A Purchase Invoice already exists for this contract: {existing_invoice}")
        else:
            create_purchase_invoice(doc)

def create_purchase_invoice(doc):
    """
    Create a Purchase Invoice using the contract data.
    """
    # Fetch total amount from the contract and set it in the Purchase Invoice
    purchase_invoice = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "supplier": doc.party_name,  # Supplier field from the contract
        "posting_date": frappe.utils.nowdate(),
        "due_date": frappe.utils.add_days(frappe.utils.nowdate(), 30),  # Example due date logic
        "items": get_contract_items(doc),  # Fetch the items from the contract
        "total": doc.total_amount,  # Assuming 'total_amount' is the total field in the contract
    })

    # Insert and submit the Purchase Invoice
    purchase_invoice.insert(ignore_permissions=True)
    purchase_invoice.submit()

def get_contract_items(doc):
    """
    Fetch service items from the contract's child table and add them to the Purchase Invoice.
    """
    items = []

    if not doc.services:  # Assuming 'services' is the child table for contract items
        frappe.throw("No service items found in the contract. Cannot create a Purchase Invoice.")

    # Iterate through the contract services and add them to the Purchase Invoice
    for service in doc.services:
        items.append({
            "item_code": service.item,  # Assuming 'item_code' exists in the services child table
            "qty": service.quantity,  # Assuming each service is billed once (quantity is 1)
            "rate": service.amount,  # Fetch the 'amount' from the service and set it as the rate
        })

    return items
