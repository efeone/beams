import frappe
from frappe import _
from frappe.model.document import Document

def set_is_edited_after_insert(doc, method):
    '''
    Sets the `is_edited` field to 0 after document insertion
    '''
    if hasattr(doc, 'is_edited'):
        doc.db_set('is_edited', 0)

def validate_customer_workflow(doc, method):
    '''
    Marks the document as edited if approved and modified after its creation date
    '''
    if doc.workflow_state == "Approved":
        creation_date = frappe.utils.get_datetime(doc.creation)
        modified_date = frappe.utils.get_datetime(doc.modified)
        
        if creation_date.date() != modified_date.date():
            if hasattr(doc, 'is_edited'):
                doc.is_edited = 1
