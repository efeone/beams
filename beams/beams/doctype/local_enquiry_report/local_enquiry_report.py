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
        'expected_completion_date': ['<=', today_date],
        'status': ['!=', 'Overdue']
    }, fields=['name', 'expected_completion_date'])

    if enquiries:
        for enquiry in enquiries:
            # Check Enquiry Completion date is set or Expected completion date is over
            if not enquiry.enquiry_completion_date and today_date > getdate(enquiry.expected_completion_date):
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

@frappe.whitelist()
def send_report_reminders():
    '''
    Send in-app notifications for reports that are incomplete 
    and nearing or past their expected completion date.
    '''
    today_date = getdate(today())
 

    # Fetch reports that are incomplete and have an expected completion date of today or earlier
    reports = frappe.get_all(
        "Local Enquiry Report",  
        filters={
            "expected_completion_date": ["<=", today_date],
            "status": ["not in", ["Completed"]],  
        },
        fields=["name", "enquiry_officer", "expected_completion_date"]
    )

    for report in reports:
   
        # Fetch Enquiry Officer's User
        user = get_enquiry_officer_user(report.enquiry_officer)

        if not user:
            continue  

        # Get last reminder date from Notification Log
        last_reminder_date = get_last_reminder_date(report.name, user)

        # Ensure reminders are only sent every two days
        if last_reminder_date and add_days(last_reminder_date, 2) > today_date:
            continue

        # Send Notification
        send_frappe_notification(report, user)

def get_enquiry_officer_user(enquiry_officer):
    '''
    Get the User linked to the Enquiry Officer (Employee) and check if they have the required role.
    '''

    if not enquiry_officer:
        return None
    
    user = frappe.get_value("Employee", enquiry_officer, "user_id")

    if not user:
        return None
    
    required_role = "Enquiry Officer"
    user_roles = frappe.get_roles(user)

    if required_role in user_roles:
        return user

    return None

def get_last_reminder_date(report_name, user):
    '''
    Fetch the last reminder date from the Notification Log for the given LER report.
    '''

    last_reminder = frappe.get_all(
        "Notification Log",
        filters={
            "subject": f"Reminder: Local Enquiry Report {report_name} is pending",
            "for_user": user
        },
        fields=["creation"],
        order_by="creation DESC",
        limit=1
    )

    if last_reminder:
        last_date = getdate(last_reminder[0].creation)
        return last_date

    return None

def send_frappe_notification(report, user):
    '''
    Create a Frappe system notification for the Enquiry Officer.
    '''
    notification_message = f"Reminder: Report {report.name} is pending. Complete it before {report.expected_completion_date}."

    notification = frappe.get_doc({
        "doctype": "Notification Log",
        "subject": f"Reminder: Local Enquiry Report {report.name} is pending",
        "email_content": notification_message,
        "for_user": user,
        "document_type": "Local Enquiry Report",  
        "document_name": report.name              
    })

    notification.insert(ignore_permissions=True)
    frappe.db.commit()

