import frappe
from frappe import _
from frappe.model.document import Document

def mark_as_edited_if_approved(doc, method):
    '''
    Marks the document as edited if approved and modified after its creation date
    '''
    if doc.workflow_state == "Approved":
        creation_date = frappe.utils.getdate(doc.creation)
        current_date = frappe.utils.getdate()

        if creation_date != current_date:
            if hasattr(doc, 'is_edited'):
                doc.is_edited = 1
