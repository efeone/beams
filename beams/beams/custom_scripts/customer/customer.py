import frappe
from frappe import _
from frappe.model.document import Document

def validate_customer_workflow(doc, method):
    '''
    Marks the document as edited if approved and modified after its creation date
    '''
    if doc.workflow_state == "Approved":
        creation_date = frappe.utils.get_datetime(doc.creation)
        current_date = frappe.utils.get_datetime(frappe.utils.now())

        if creation_date.date() != current_date.date():
            if hasattr(doc, 'is_edited'):
                doc.is_edited = 1
