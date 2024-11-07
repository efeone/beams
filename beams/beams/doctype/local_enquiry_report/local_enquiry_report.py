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
        self.information_required()
        self.set_expected_completion_date()

        """Ensure enquiry officer selection based on workflow state."""
        # Ensure enquiry officer selection based on workflow state.
        if self.workflow_state == 'Assign to Enquiry Officer':
            if not self.enquiry_officer:
                frappe.msgprint(_("Please select an enquiry officer before proceeding."))

    def on_submit(self):
        if self.docstatus == 1:
            update_job_applicant_status(self.name)

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

            # Ensure enquiry officer selection based on workflow state.
            if self.workflow_state == 'Assign to Enquiry Officer':
                if not self.enquiry_officer:
                    frappe.msgprint(_("Please select an enquiry officer before proceeding."))

            if len(missing_fields) == 2:
                frappe.throw("Please provide 'Information given by' and 'Information given by Designation' before completing the report.")

            elif missing_fields:
                frappe.throw(f"Please provide '{', '.join(missing_fields)}' before completing the report.")

    def on_update(doc):
        """Handle workflow transitions upon document update."""
        try:
            if doc.workflow_state == "Assigned to Admin":
                assign_to_enquiry_manager(doc)

            elif doc.workflow_state == "Assigned to Enquiry Officer":
                assign_to_enquiry_officer(doc)
                remove_enquiry_manager_assignment(doc)

            elif doc.workflow_state == "Enquiry on Progress":
                set_enquiry_start_date(doc)

            elif doc.workflow_state == "Pending Approval":
                set_enquiry_completion_date(doc)

        except Exception as e:
            frappe.throw(_("Error in workflow processing: {0}").format(str(e)))


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
                frappe.db.commit()  # Commit the changes to the database

    frappe.msgprint("Overdue status has been updated for applicable Local Enquiry Reports.")

@frappe.whitelist()
def update_job_applicant_status(local_enquiry_report):

    '''
    This function retrieves the specified Local Enquiry Report and, if a Job Applicant is linked to it,
    updates the applicant's status to "Local Enquiry Approved" and saves the changes.
    '''
    report = frappe.get_doc("Local Enquiry Report", local_enquiry_report)
    job_applicant = report.job_applicant
    designation = report.designation
    if job_applicant:
        applicant_doc = frappe.get_doc("Job Applicant", job_applicant)
        applicant_doc.status = "Local Enquiry Approved"
        applicant_doc.save()
        frappe.msgprint(f"Status of Job Applicant {applicant_doc.name} updated to 'Local Enquiry Approved'.")


@frappe.whitelist()
def assign_to_enquiry_manager(doc):
    """Assign LER to the Enquiry Manager role."""
    try:
        # Use get_users_with_role to get users with the "Enquiry Manager" role
        managers = get_users_with_role("Enquiry Manager")

        if not managers:
            frappe.throw(_("No users found with the 'Enquiry Manager' role."))

        # Use the first user from the list for the assignment
        manager_id = managers[0]

        # Assign the task using add_assign
        add_assign({
            "assign_to": [manager_id],
            "doctype": "Local Enquiry Report",
            "name": doc.name,
            "description": "Please review and assign to an Enquiry Officer."
        })

        frappe.msgprint(_("Enquiry Manager has been Assigned."))

    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
def assign_to_enquiry_officer(doc):
    """Assign LER to the selected Enquiry Officer."""
    try:
        # Fetch user ID of the enquiry officer
        user_id = frappe.db.get_value("Employee", {"name": doc.enquiry_officer}, "user_id")

        if not user_id or not frappe.db.exists("User", user_id):
            frappe.throw(_("The selected enquiry officer is not a valid user."))

        # Validate if the user has the role of Enquiry Officer
        enquiry_officers = get_users_with_role("Enquiry Officer")
        if user_id not in enquiry_officers:
            frappe.throw(_("The selected enquiry officer does not have the 'Enquiry Officer' role."))

        # Use add_assign to create the assignment
        add_assign({
            "assign_to": [user_id],
            "doctype": "Local Enquiry Report",
            "name": doc.name,
            "description": "Local enquiry assigned to you for investigation.",
        })

        frappe.msgprint(_("Assigned to Enquiry Officer successfully."))
    except Exception as e:
        frappe.throw(_("An error occurred while assigning to Enquiry Officer: {0}").format(str(e)))


@frappe.whitelist()
def remove_enquiry_manager_assignment(doc):
    """Remove the assignment from the Enquiry Manager for this LER document."""
    try:
        # Ensure the document is fetched correctly
        if not isinstance(doc, Document):
            doc = frappe.get_doc("Local Enquiry Report", doc)

        # Define the unique description for the task assignment
        manager_assignment_description = "Please review and assign to an Enquiry Officer."

        # Fetch the ToDo task linked to the document with the description for the Enquiry Manager
        todo = frappe.db.get_value(
            "ToDo",
            {
                "reference_type": "Local Enquiry Report",
                "reference_name": doc.name,
                "description": manager_assignment_description,
                "status": "Open"
            },
            "name"
        )

        # If the ToDo exists, remove the assignment
        if todo:
            assigned_user = frappe.db.get_value("ToDo", todo, "allocated_to")
            if assigned_user:
                remove_assign(
                    doctype="Local Enquiry Report",
                    name=doc.name,
                    assign_to=assigned_user
                )
    except Exception as e:
        frappe.throw(_("Error while removing assignment: {0}").format(str(e)))

@frappe.whitelist()
def set_enquiry_start_date(doc):
    """
    This function checks if the 'enquiry_start_date' is empty or not. If it is not set,
    the function assigns the current date to the field and saves the document.
    """

    if not doc.enquiry_start_date:
        doc.enquiry_start_date = nowdate()
        doc.save(ignore_permissions=True)


@frappe.whitelist()
def set_enquiry_completion_date(doc):
    """
    This function checks if the 'enquiry_completion_date' is empty or not. If it is not set,
    the function assigns the current date to the field and saves the document.
    """
    if not doc.enquiry_completion_date:
        doc.enquiry_completion_date = nowdate()
        doc.save(ignore_permissions=True)
@frappe.whitelist()
def get_enquiry_officers(doctype, txt, searchfield, start, page_len, filters):
    """
    Fetch employees with the 'Enquiry Officer' role.

    Args:
        doctype (str): The doctype being searched
        txt (str): Search text
        searchfield (str): Field being searched
        start (int): Starting index for pagination
        page_len (int): Number of records per page
        filters (dict): Additional filters including role

    Returns:
        list: List of tuples containing employee code and name
    """
    role_filter = filters.get('role', 'Enquiry Officer')

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
        'role': role_filter,
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

    # Handle no results case
    if not officers:
        frappe.throw(
            _("No Enquiry Officers found with the role '{0}' or the specified criteria.")
            .format(role_filter)
        )

    return officers
