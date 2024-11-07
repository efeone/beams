# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, today

class LocalEnquiryReport(Document):
    def validate(self):
        self.information_required()
        self.set_expected_completion_date()
        self.information_required()

    def on_update(self):
        if self.workflow_state == "Approved":
            update_job_applicant_status(self.name, "Local Enquiry Approved")
        elif self.workflow_state == "Enquiry on Progress":
            update_job_applicant_status(self.name, "Local Enquiry Started")
        elif self.workflow_state == "Pending Approval":
            update_job_applicant_status(self.name, "Local Enquiry Completed")
        elif self.workflow_state == "Rejected":
            update_job_applicant_status(self.name, "Local Enquiry Rejected")

    def information_required(self):
        """
        Validation for the missing fields -> information_given_by and information_given_by_designation
        """
        if self.workflow_state == "Pending Approval":
            if frappe.session.user:
                self.information_collected_by = frappe.session.user

            missing_fields = []

            if not self.information_given_by:
                missing_fields.append("Information given by")
            if not self.information_given_by_designation:
                missing_fields.append("Information given by Designation")

            if len(missing_fields) == 2:
                frappe.throw("Please provide 'Information given by' and 'Information given by Designation' before completing the report.")

            elif missing_fields:
                frappe.throw(f"Please provide '{', '.join(missing_fields)}' before completing the report.")

    def set_expected_completion_date(self):
        """
        Set 'Expected Completion Date' based on the default enquiry duration when workflow state is 'Assigned to Enquiry Officer'
        """
        if self.workflow_state == "Assigned to Enquiry Officer":
            # Fetch the default local enquiry duration, use 0 if unset
            default_duration = frappe.db.get_single_value("Beams HR Settings", "default_local_enquiry_duration") or 0

            # Set Expected Completion Date as today’s date plus the default duration
            self.expected_completion_date = add_days(today(), int(default_duration))

@frappe.whitelist()
def set_status_to_overdue():
    '''
    This function updates the status of Local Enquiry Reports. It sets the status to 'Overdue' for reports where the expected completion date is today or earlier,
    the enquiry completion date is not set or is later than the expected completion date, and the current status is not already 'Overdue'.
    '''
    today_date = getdate(today())

    # Fetch Local Enquiry Reports with expected completion date on or before today and status not set to 'Overdue'
    enquiries = frappe.get_all('Local Enquiry Report', filters={
        'expected_completion_date': ['<=', today_date],
        'status': ['!=', 'Overdue']
    }, fields=['name', 'expected_completion_date', 'enquiry_completion_date'])

    if enquiries:
        for enquiry in enquiries:
            # Check if 'Enquiry Completion Date' is not set or is later than 'Expected Completion Date'
            if not enquiry.enquiry_completion_date or getdate(enquiry.enquiry_completion_date) > getdate(enquiry.expected_completion_date):
                frappe.db.set_value('Local Enquiry Report', enquiry.name, 'status', 'Overdue')

        frappe.db.commit()

def update_job_applicant_status(local_enquiry_report, status=None):
    '''
    This function retrieves the specified Local Enquiry Report and, if a Job Applicant is linked to it,
    updates the applicant's status based on the provided status and saves the changes.
    If no status is provided, it checks the status from the workflow state.
    '''
    report = frappe.get_doc("Local Enquiry Report", local_enquiry_report)
    job_applicant = report.job_applicant

    if job_applicant:
        applicant_doc = frappe.get_doc("Job Applicant", job_applicant)

        if status:
            applicant_doc.status = status
        else:
            # Set the status based on the workflow state (you can modify these conditions)
            if report.workflow_state == "Approved":
                applicant_doc.status = "Local Enquiry Approved"
            if report.workflow_state == "Enquiry on Progress":
                applicant_doc.status = "Local Enquiry Started"
            elif report.workflow_state == "Pending Approval":
                applicant_doc.status = "Local Enquiry Completed"
            elif report.workflow_state == "Rejected":
                applicant_doc.status = "Local Enquiry Rejected"

        applicant_doc.save()
        frappe.msgprint(f"Status of Job Applicant {applicant_doc.name} updated to '{applicant_doc.status}'.")
