# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class LocalEnquiryReport(Document):
    pass

@frappe.whitelist()
def set_status_to_overdue():
    """
     This function updates the status of Local Enquiry Reports. It sets the status to 'Overdue'for reports where the expected completion date is today or earlier,
     the enquiry completion date is not set or is later than the expected completion date, and the current status is not already 'Overdue'.
    """
    today = getdate(frappe.utils.today())

    # Fetch Local Enquiry Reports with expected completion date on or before today and status not set to 'Overdue'
    enquiries = frappe.get_all('Local Enquiry Report', filters={
        'expected_completion_date': ['<=', today],
        'status': ['!=', 'Overdue']
    }, fields=['name', 'expected_completion_date', 'enquiry_completion_date'])

    if enquiries:
        for enquiry in enquiries:
            doc = frappe.get_doc('Local Enquiry Report', enquiry.name)
            # Check if 'Enquiry Completion Date' is not set or is later than 'Expected Completion Date'
            if not doc.enquiry_completion_date or getdate(doc.enquiry_completion_date) > getdate(doc.expected_completion_date):
                frappe.db.set_value('Local Enquiry Report', enquiry.name, 'status', 'Overdue')

        frappe.db.commit()
