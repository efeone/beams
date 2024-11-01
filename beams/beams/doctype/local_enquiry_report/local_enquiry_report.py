# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class LocalEnquiryReport(Document):
    def validate(self):
         self.information_required()

    
    def information_required(self):
        """
        Validation for the missing fields -> information_given_by and information_given_by_designation 
        """
        if self.workflow_state == "Pending Approval":
            missing_fields = []

            if not self.information_given_by:
                missing_fields.append("Information given by")
            if not self.information_given_by_designation:
                missing_fields.append("Information given by Designation")

            if len(missing_fields) == 2:
                frappe.throw("Please provide 'Information given by' and 'Information given by Designation' before completing the report.")
            
            elif missing_fields:
                frappe.throw(f"Please provide '{', '.join(missing_fields)}' before completing the report.")


@frappe.whitelist()
def set_status_to_overdue():
    '''
     This function updates the status of Local Enquiry Reports. It sets the status to 'Overdue'for reports where the expected completion date is today or earlier,
     the enquiry completion date is not set or is later than the expected completion date, and the current status is not already 'Overdue'.
    '''
    today = getdate(frappe.utils.today())

    # Fetch Local Enquiry Reports with expected completion date on or before today and status not set to 'Overdue'
    enquiries = frappe.get_all('Local Enquiry Report', filters={
        'expected_completion_date': ['<=', today],
        'status': ['!=', 'Overdue']
    }, fields=['name', 'expected_completion_date', 'enquiry_completion_date'])

    if enquiries:
        for enquiry in enquiries:
            # Check if 'Enquiry Completion Date' is not set or is later than 'Expected Completion Date'
            if not enquiry.enquiry_completion_date or getdate(enquiry.enquiry_completion_date) > getdate(enquiry.expected_completion_date):
                frappe.db.set_value('Local Enquiry Report', enquiry.name, 'status', 'Overdue')

        frappe.db.commit()


