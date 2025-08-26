# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, get_datetime
from frappe import _

class ExternalResourceRequest(Document):

	def validate(self):
		self.validate_required_from_and_required_to()

	def before_save(self):
		self.validate_posting_date()

	def on_submit(self):
		self.update_external_resources_project_allocated_resources()
		self.update_hired_field()
		self.update_technical_req()

	def update_external_resources_project_allocated_resources(self):
		"""Update the allocated_manpower_details table in Project when a External Resource Request is Submitted."""
		if not frappe.db.exists('Project', self.project):
			frappe.throw(_("Invalid Project ID: {0}").format(self.project))

		project = frappe.get_doc('Project', self.project)

		allocated_resources = [
			{
				"department": req.department,
				"designation": req.designation,
				"assigned_from": get_datetime(req.required_from) if req.required_from else None,
				"assigned_to": get_datetime(req.required_to) if req.required_to else None,
				"hired_personnel": req.hired_personnel,
				"hired_personnel_contact_info": req.contact_number
			}
			for req in self.get("required_resources", [])
		]

		if allocated_resources:
			project.extend("allocated_manpower_details", allocated_resources)
			project.save(ignore_permissions=True)

	@frappe.whitelist()
	def validate_required_from_and_required_to(self):
		"""Validates required_from and required_to dates."""
		if not self.required_from or not self.required_to:
			return

		required_from = getdate(self.required_from)
		required_to = getdate(self.required_to)

		if required_from > required_to:
			frappe.throw(
				msg=_('The "Required From" date cannot be after the "Required To" date.'),
				title=_('Validation Error')
			)

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			posting_date = getdate(self.posting_date)
			today_date = getdate(today())
			if posting_date > today_date:
				frappe.throw(_("Posting Date cannot be set after today's date."))

	@frappe.whitelist()
	def updated_required_resources(self):
		"""Sync parent dates into child table required_resources"""
		for req in self.required_resources:
			req.required_from = self.required_from
			req.required_to = self.required_to

	@frappe.whitelist()
	def update_hired_field(self):
		"""Update manpower status in Project when External Resource Request is submitted"""
		if self.project:
			project = frappe.get_doc("Project", self.project)

			# Ensure required tables exist
			if not hasattr(self, "required_resources") or not hasattr(project, "allocated_manpower_details"):
				frappe.throw("Required tables are missing in the External Resource Request or Project doctype.")

			for resource in self.required_resources:
				for manpower in project.allocated_manpower_details:
					if (
						resource.designation == manpower.designation
						and resource.hired_personnel == manpower.hired_personnel
						and get_datetime(resource.required_from) == get_datetime(manpower.assigned_from)
						and get_datetime(resource.required_to) == get_datetime(manpower.assigned_to)
					):
						manpower.status = 'Hired'

			project.save(ignore_permissions=True)
			frappe.msgprint(f"Hired manpower updated for Project {self.project}")

	@frappe.whitelist()
	def update_technical_req(self):
		"""Sync hired_personnel from External Resource Request → Technical Request"""
		if not self.technical_request:
			return

		tech_req = frappe.get_doc("Technical Request", self.technical_request)

		if not hasattr(self, "required_resources") or not hasattr(tech_req, "required_employees"):
			frappe.throw("Required tables are missing in the External Resource Request or Technical Request doctype.")

		for resource in self.required_resources:
			if resource.hired_personnel and resource.technical_request_employee:
				emp_row = frappe.get_doc("Technical Request Details", resource.technical_request_employee)
				emp_row.hired_personnel = resource.hired_personnel
				emp_row.save(ignore_permissions=True)

		tech_req.reload()
		frappe.msgprint(f"Hired Personnel synced to Technical Request {tech_req.name}")
