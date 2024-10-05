import frappe
from frappe import _

def before_save(doc, method):
    """
    Updates the document status based on its workflow state.
    Allows changes unless the document is in a final state, with "Cancelled" as an exception.
    """
    workflow_to_status = {
        "Draft": "Pending",
        "Pending Approval": "Pending",
        "Approved": "Open & Approved",
        "Rejected": "Rejected",
        "On Hold": "On Hold",
        "Cancelled": "Cancelled"
    }
    final_statuses = ["Open & Approved", "Rejected", "Filled", "On Hold"]

    if doc.workflow_state == "Cancelled":
        doc.status = "Cancelled"
    # Update status only if not in a final state
    elif doc.status not in final_statuses:
        doc.status = workflow_to_status.get(doc.workflow_state, doc.status)
