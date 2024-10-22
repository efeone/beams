# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class LocalEnquiryReport(Document):
    pass


@frappe.whitelist()
def update_local_enquiry_status():
    '''
    This function updates the status of Local Enquiry Reports. It sets the status to 'Overdue'for reports where the expected completion date is today or earlier,
    the enquiry completion date is not set or is later than the expected completion date, and the current status is not already 'Overdue'.
    '''
    today = getdate()
    enquiries = frappe.get_all('Local Enquiry Report', filters={
        'expected_completion_date': ['<=', today],
        'status': ['!=', 'Overdue']
    })
    for enquiry in enquiries:
        if frappe.db.exists("Local Enquiry Report", enquiry.name):
            doc = frappe.get_doc('Local Enquiry Report', enquiry.name)
            if not doc.enquiry_completion_date or doc.enquiry_completion_date > doc.expected_completion_date:
                doc.status = 'Overdue'  # Set status to 'Overdue'
                doc.save()  # Save the document
