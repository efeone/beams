# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate
from frappe.utils import get_url_to_form
from frappe.desk.form.assign_to import add as add_assign, remove as remove_assign
from frappe.utils.user import get_users_with_role
from frappe.email.doctype.notification.notification import get_context

@frappe.whitelist()
def remove_assignment_by_role(doc, role):
    """
    Removes ToDo assignments for users with a specific role for a given document.
    """
    users = get_users_with_role(role)
    if users:
        for user in users:
            if frappe.db.exists('ToDo', {
                'reference_type': doc.doctype,
                'reference_name': doc.name,
                'allocated_to': user,
                'status': 'Open'
            }):
                remove_assign(
                    doctype=doc.doctype,
                    name=doc.name,
                    assign_to=user
                )

class JobProposal(Document):
    def on_update(self):
        self.create_todo_on_pending_approval()

    def create_offer_from_job_proposal(self):
        '''
        Create a Job Offer when the Job Proposal is approved.
        '''
        if self.workflow_state == "Applicant Accepted":
            job_offer = frappe.new_doc('Job Offer')
            job_offer.job_applicant = self.job_applicant
            job_offer.designation = self.designation
            job_offer.offer_date = getdate(today())
            job_offer.job_proposal = self.name
            job_offer.ctc = self.proposed_ctc
            job_offer.job_offer_term_template = self.job_offer_term_template
            job_offer.select_terms = self.terms_and_conditions
            job_offer.flags.ignore_mandatory = True
            job_offer.flags.ignore_validate = True
            job_offer.insert()
            job_offer.submit()
            frappe.msgprint('Job Offer Created: <a href="{0}">{1}</a>'.format(get_url_to_form(job_offer.doctype, job_offer.name), job_offer.name), alert=True, indicator='green')

            beams_hr_settings = frappe.get_doc("Beams HR Settings")
            job_applicant_doc = frappe.get_doc('Job Applicant', self.job_applicant)
            context = get_context(job_applicant_doc)
            if beams_hr_settings.admin_hod and beams_hr_settings.notification_to_admin:
                # Admin HOD Assignment
                if frappe.db.exists('Employee', beams_hr_settings.admin_hod):
                    admin_user = frappe.db.get_value('Employee', beams_hr_settings.admin_hod, 'user_id')
                    if admin_user:
                        admin_message = frappe.render_template(beams_hr_settings.notification_to_admin, context)
                        add_assign({
                            "assign_to": [admin_user],
                            "doctype": "Job Applicant",
                            "name": self.job_applicant,
                            "description": admin_message
                        })
                # IT HOD Assignment
                if frappe.db.exists('Employee', beams_hr_settings.it_hod):
                    it_user = frappe.db.get_value('Employee', beams_hr_settings.it_hod, 'user_id')
                    if it_user:
                        it_message = frappe.render_template(beams_hr_settings.notification_to_it, context)
                        add_assign({
                            "assign_to": [it_user],
                            "doctype": "Job Applicant",
                            "name": self.job_applicant,
                            "description": it_message
                        })

    def on_update_after_submit(self):
        """
        Updates the status of the linked Job Applicant document to "Applicant Accepted"
        when the Job Proposal workflow state changes to "Applicant Accepted".
        """
        self.create_offer_from_job_proposal()
        self.create_todo_on_verified_by_ceo()
        if self.workflow_state == "Applicant Accepted":
            if self.job_applicant:
                if frappe.db.exists("Job Applicant", self.job_applicant):
                    job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
                    job_applicant.status = "Job Proposal Accepted"
                    job_applicant.save()
        if self.workflow_state in ["Approved", "Rejected"]:
            remove_assignment_by_role(self, "CEO")

    def after_insert(self):
        """Set the corresponding Job Applicant's status to 'Job Proposal Created' when a Job Proposal is created."""
        if self.job_applicant:
            if frappe.db.exists("Job Applicant", self.job_applicant):
                job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
                job_applicant.status = "Job Proposal Created"
                job_applicant.save()

    def create_todo_on_pending_approval(self):
        """
        Creates a ToDo task for CEO Users when a new Job Proposal is created.
        Ensures that each CEO User gets a task to review and update the new job proposal.
        """
        users = get_users_with_role("CEO")
        if users:
            description = f"New Job Proposal Created for {self.job_applicant}. Please review and update details or take necessary actions."
            for user in users:
                if not frappe.db.exists('ToDo', {'reference_name': self.name, 'assign_to': user}):
                    add_assign({
                        "assign_to": [user],
                        "doctype": "Job Proposal",
                        "name": self.name,
                        "description": description
                    })

    def create_todo_on_verified_by_ceo(self):
        """
        Creates a ToDo task for the HR Manager based on the workflow state of the Job Proposal.
        - If the state is "Approved", creates a task for the HR Manager to proceed with the next step.
        - If the state is "Rejected", creates a task for the HR Manager to review and revise or proceed with feedback.
        """
        if self.workflow_state == "Approved":
            hr_manager_users = get_users_with_role("HR Manager")
            if hr_manager_users:
                description = f"Approved by CEO: Job Proposal for {self.job_applicant}. Please proceed with the next step."
                if not frappe.db.exists('ToDo', {'reference_name': self.name, 'reference_type': 'Job Proposal', 'description': description}):
                    add_assign({
                        "assign_to": hr_manager_users,
                        "doctype": "Job Proposal",
                        "name": self.name,
                        "description": description
                    })
        elif self.workflow_state == "Rejected":
            hr_manager_users = get_users_with_role("HR Manager")
            if hr_manager_users:
                description = f"Rejected by CEO: Job Proposal for {self.job_applicant}. Please review and revise, or proceed with their feedback."
                if not frappe.db.exists('ToDo', {'reference_name': self.name, 'reference_type': 'Job Proposal', 'description': description}):
                    add_assign({
                        "assign_to": hr_manager_users,
                        "doctype": "Job Proposal",
                        "name": self.name,
                        "description": description
                    })
