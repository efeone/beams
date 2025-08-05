# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, today, nowdate
from frappe import _
from frappe.utils.user import get_users_with_role
from frappe.desk.form.assign_to import add as add_assign
from frappe.desk.form.assign_to import remove as remove_assign

class LocalEnquiryReport(Document):
    def validate(self):
        self.validate_informations_provided()
        self.validate_enquiry_officer()
        self.set_expected_completion_date()
        self.set_status_complted()

    def on_submit(self):
       update_job_applicant_status(self.job_applicant, 'Local Enquiry Approved')

    def validate_enquiry_officer(self):
        '''
            Ensure Enquiry Officer selection based on workflow state
        '''
        if self.workflow_state == 'Assigned to Enquiry Officer':
            if not self.enquiry_officer:
                frappe.throw(_('Please select an enquiry officer before proceeding.'))

    def validate_informations_provided(self):
        '''
            Method to validate required fields before Pending Approval
        '''
        if self.workflow_state == 'Pending Approval':
            if frappe.session.user:
                # Setting Logged In user as information_collected_by
                self.information_collected_by = frappe.session.user

            if not self.information_given_by:
                frappe.throw('`Information Given By : Person Name` is required before Sending for Approval')

            if not self.information_given_by_designation:
                frappe.throw('`Information Given By : Designation` is required before Sending for Approval')

            if not self.enquiry_report:
                frappe.throw('`Enquiry Report` is required before Sending for Approval')

    def set_status_complted(self):
        '''
            Automatically set the status to 'Completed' when enquiry_completion_date is set.
        '''
        if self.enquiry_completion_date and self.status != 'Completed':
            self.status = 'Completed'

    def on_update(self):
        '''
            Method trigger on on_update event to perform actions
        '''
        if self.workflow_state == 'Assigned to Admin':
            todo_message = "Please review and assign to an Enquiry Officer"
            assign_doc_by_role(self, 'Enquiry Manager', todo_message)

        elif self.workflow_state == 'Assigned to Enquiry Officer':
            #Remove Enquiry Manager Assignment
            remove_assignment_by_role(self, 'Enquiry Manager')

            #Assign to Enquiry Officer if not exists
            if self.enquiry_officer:
                user_id = frappe.db.get_value('Employee', self.enquiry_officer , 'user_id')
                todo_message = "Local enquiry assigned to you for investigation"
                todos = get_assignments_with_message(self, todo_message)
                if user_id and not todos:
                    add_assign({
                        "assign_to": [user_id],
                        "doctype": self.doctype,
                        "name": self.name,
                        "description": todo_message,
                    })

        elif self.workflow_state == 'Enquiry on Progress':
            update_job_applicant_status(self.job_applicant, 'Local Enquiry Started')
            self.set_enquiry_start_date()

        elif self.workflow_state == 'Pending Approval':
            update_job_applicant_status(self.job_applicant, 'Local Enquiry Completed')
            self.set_enquiry_completion_date()

        elif self.workflow_state == 'Rejected':
            update_job_applicant_status(self.job_applicant, 'Local Enquiry Rejected')

    def set_expected_completion_date(self):
        '''
            Set `Expected Completion Date based on the default enquiry duration when workflow state is `Assigned to Enquiry Officer`
        '''
        if self.workflow_state == 'Assigned to Enquiry Officer':
            default_duration = frappe.db.get_single_value('Beams HR Settings', 'default_local_enquiry_duration') or 0
            # Set Expected Completion Date as today’s date plus the default duration
            self.expected_completion_date = add_days(today(), int(default_duration))

    def set_enquiry_start_date(self):
        '''
            Method to set `enquiry_start_date` is not set
        '''
        if not self.enquiry_start_date:
            self.enquiry_start_date = nowdate()
            self.save(ignore_permissions=True)

    def set_enquiry_completion_date(self):
        '''
            Method to set `enquiry_completion_date` is not set
        '''
        if not self.enquiry_completion_date:
            self.enquiry_completion_date = nowdate()
            self.save(ignore_permissions=True)

def update_job_applicant_status(job_applicant, status):
    '''
        Method to set Job Applicant Status
    '''
    if frappe.db.exists('Job Applicant', job_applicant):
        frappe.db.set_value('Job Applicant', job_applicant, 'status', status)

@frappe.whitelist()
def set_status_to_overdue():
    '''
        This function updates the status of Local Enquiry Reports. It sets the status to 'Overdue' for reports where the expected completion date is today or earlier,
        the enquiry completion date is not set or is later than the expected completion date, and the current status is not already 'Overdue'.
    '''
    today_date = getdate(today())

    # Fetch Local Enquiry Reports with expected completion date on or before today and status not set to 'Overdue'
    enquiries = frappe.get_all('Local Enquiry Report', filters={
        'status': ['!=', 'Overdue']
    }, fields=['name', 'expected_completion_date','enquiry_completion_date'])
    

    if enquiries:
        for enquiry in enquiries:
            expected_date = getdate(enquiry.expected_completion_date)if enquiry.expected_completion_date else None
            completion_date = getdate(enquiry.enquiry_completion_date) if enquiry.enquiry_completion_date else None
            if not expected_date:
                continue
            if expected_date and expected_date < today_date and not completion_date  :
                frappe.db.set_value('Local Enquiry Report', enquiry.name, 'status', 'Overdue')





@frappe.whitelist()
def assign_doc_by_role(doc, role, message):
    '''
        Method to create assignemnt to a doc with specific Role
    '''
    users = get_users_with_role(role)
    if users:
        todos = get_assignments_with_message(doc, message)
        if not todos:
            add_assign({
                "assign_to": users,
                "doctype": doc.doctype,
                "name": doc.name,
                "description": message
            })

def get_assignments_with_message(doc, message):
    '''
        Get assignments with Role
    '''
    todos = frappe.db.get_all('ToDo', {
        'reference_type':doc.doctype,
        'reference_name':doc.name,
        'status': 'Open',
        'description': message
    })
    return todos

@frappe.whitelist()
def remove_assignment_by_role(doc, role):
    users = get_users_with_role(role)
    if users:
        for user in users:
            if frappe.db.exists('ToDo', { 'reference_type': doc.doctype, 'reference_name':doc.name, 'allocated_to':user, 'status':'Open' }):
                remove_assign(
                    doctype = doc.doctype,
                    name = doc.name,
                    assign_to = user
                )

@frappe.whitelist()
def enquiry_officer_query(doctype, txt, searchfield, start, page_len, filters):
    '''
        Enquiry Officer filter query
    '''
    role_name = 'Enquiry Officer'
    query = """
        SELECT
            emp.name,
            emp.employee_name
        FROM
            `tabEmployee` emp
            INNER JOIN `tabUser` u
                ON u.name = emp.user_id
            INNER JOIN `tabHas Role` hr
                ON hr.parent = u.name
        WHERE
            hr.role = %(role)s
            AND emp.status = 'Active'
            AND (
                emp.name LIKE %(search_txt)s
                OR emp.employee_name LIKE %(search_txt)s
            )
        LIMIT %(start)s, %(page_len)s
    """

    # Prepare query parameters
    params = {
        'role': role_name,
        'search_txt': f"%{txt}%",
        'start': start,
        'page_len': page_len
    }

    # Execute query
    officers = frappe.db.sql(
        query,
        params,
        as_list=True
    )
    return officers
