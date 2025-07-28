# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate
from frappe.utils import get_url_to_form
from frappe.desk.form.assign_to import add as add_assign, remove as remove_assign
from frappe.utils.user import get_users_with_role
from frappe.email.doctype.notification.notification import get_context

class CompensationProposal(Document):
	def on_update(self):
		self.create_todo_on_pending_approval()

	def validate(self):
		self.set_payslips_from_job_applicant()
		self.validate_proposed_ctc()

	def create_offer_from_compensation_proposal(self):
		'''
		Create a Job Offer when the Compensation Proposal is approved.
		'''
		if self.workflow_state == "Applicant Accepted":
			job_offer = frappe.new_doc('Job Offer')
			job_offer.job_applicant = self.job_applicant
			job_offer.designation = self.designation
			job_offer.offer_date = getdate(today())
			job_offer.compensation_proposal = self.name
			job_offer.ctc = self.proposed_ctc
			job_offer.job_offer_term_template = self.job_offer_term_template
			job_offer.select_terms = self.terms_and_conditions

			if self.terms_and_conditions and frappe.db.exists('Terms and Conditions', self.terms_and_conditions):
				terms_template = frappe.db.get_value('Terms and Conditions', self.terms_and_conditions, "terms")
				job_applicant_doc = frappe.get_doc('Job Applicant', self.job_applicant)
				job_offer.terms = frappe.render_template(terms_template, get_context(job_applicant_doc))

			if self.job_offer_term_template and frappe.db.exists('Job Offer Term Template', self.job_offer_term_template):
				template = frappe.get_doc('Job Offer Term Template', self.job_offer_term_template)
				for term in template.offer_terms:
					job_offer.append('offer_terms', {
						'offer_term': term.offer_term,
						'value': term.value
					})

			job_offer.flags.ignore_mandatory = True
			job_offer.flags.ignore_validate = True
			job_offer.insert()
			job_offer.submit()

			frappe.msgprint(
				'Job Offer Created: <a href="{0}">{1}</a>'.format(
					get_url_to_form(job_offer.doctype, job_offer.name),
					job_offer.name
				),
				alert=True,
				indicator='green'
			)

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
		when the Compensation Proposal workflow state changes to "Applicant Accepted".
		"""
		self.create_offer_from_compensation_proposal()
		self.create_todo_on_verified_by_ceo()
		if self.workflow_state == "Applicant Accepted":
			if self.job_applicant:
				if frappe.db.exists("Job Applicant", self.job_applicant):
					job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
					job_applicant.status = "Compensation Proposal Accepted"
					job_applicant.save()
		if self.workflow_state in ["Approved", "Rejected"]:
			remove_assignment_by_role(self, "CEO")

	def after_insert(self):
		"""Set the corresponding Job Applicant's status to 'Compensation Proposal Created' when a Compensation Proposal is created."""
		if self.job_applicant:
			if frappe.db.exists("Job Applicant", self.job_applicant):
				job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
				job_applicant.status = "Compensation Proposal Created"
				job_applicant.save()

	def create_todo_on_pending_approval(self):
		"""
		Creates a ToDo task for CEO Users when a new Compensation Proposal is created.
		Ensures that each CEO User gets a task to review and update the new Compensation Proposal.
		"""
		users = get_users_with_role("CEO")
		if users:
			description = f"New Compensation Proposal Created for {self.job_applicant}. Please review and update details or take necessary actions."
			for user in users:
				if not frappe.db.exists('ToDo', {'reference_name': self.name, 'assign_to': user}):
					add_assign({
						"assign_to": [user],
						"doctype": "Compensation Proposal",
						"name": self.name,
						"description": description
					})

	def create_todo_on_verified_by_ceo(self):
		"""
		Creates a ToDo task for the HR Manager based on the workflow state of the Compensation Proposal.
		- If the state is "Approved", creates a task for the HR Manager to proceed with the next step.
		- If the state is "Rejected", creates a task for the HR Manager to review and revise or proceed with feedback.
		"""
		if self.workflow_state == "Approved":
			hr_manager_users = get_users_with_role("HR Manager")
			if hr_manager_users:
				description = f"Approved by CEO: Compensation Proposal for {self.job_applicant}. Please proceed with the next step."
				if not frappe.db.exists('ToDo', {'reference_name': self.name, 'reference_type': 'Compensation Proposal', 'description': description}):
					add_assign({
						"assign_to": hr_manager_users,
						"doctype": "Compensation Proposal",
						"name": self.name,
						"description": description
					})
		elif self.workflow_state == "Rejected":
			hr_manager_users = get_users_with_role("HR Manager")
			if hr_manager_users:
				description = f"Rejected by CEO: Compensation Proposal for {self.job_applicant}. Please review and revise, or proceed with their feedback."
				if not frappe.db.exists('ToDo', {'reference_name': self.name, 'reference_type': 'Compensation Proposal', 'description': description}):
					add_assign({
						"assign_to": hr_manager_users,
						"doctype": "Compensation Proposal",
						"name": self.name,
						"description": description
					})

	@frappe.whitelist()
	def validate_proposed_ctc(self):
		"""
		Validate that the proposed CTC value is not negative.
		"""
		if self.proposed_ctc < 0:
			frappe.throw("Proposed CTC cannot be a Negative value")


	def set_payslips_from_job_applicant(self):
		"""
		Fetch payslip_month_1, payslip_month_2, and payslip_month_3 from Job Applicant
		and set them in the Compensation Proposal.
		"""
		if self.job_applicant and frappe.db.exists("Job Applicant", self.job_applicant):
			job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
			self.payslip_month_1 = job_applicant.payslip_month_1
			self.payslip_month_2 = job_applicant.payslip_month_2
			self.payslip_month_3 = job_applicant.payslip_month_3

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

