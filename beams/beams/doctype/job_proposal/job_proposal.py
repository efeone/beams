# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate
from frappe.utils import get_url_to_form
from frappe.desk.form.assign_to import add as add_assign
from frappe.email.doctype.notification.notification import get_context


class JobProposal(Document):
	def on_update_after_submit(self):
		self.create_offer_from_job_proposal()

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
		if self.workflow_state == "Applicant Accepted":
				if self.job_applicant:
					if frappe.db.exists("Job Applicant", self.job_applicant):
						job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
						job_applicant.status = "Job Proposal Accepted"
						job_applicant.save()


	def after_insert(self):
	    """Set the corresponding Job Applicant's status to 'Job Proposal Created' when a Job Proposal is created."""
	    if self.job_applicant:
 		   if frappe.db.exists("Job Applicant", self.job_applicant):
 			   job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
 			   job_applicant.status = "Job Proposal Created"
 			   job_applicant.save()
