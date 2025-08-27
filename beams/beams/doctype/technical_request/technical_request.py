# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate,format_date
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today
from frappe.utils import get_datetime
from datetime import datetime

class TechnicalRequest(Document):
	def before_save(self):
		self.validate_posting_date()

	def validate(self):
		self.validate_required_from_and_required_to()
		if self.workflow_state == "Allocated by HOD":
			self.validate_employee_before_approvel()
			self.validate_employee_assignment()
			self.validate_employee_assignment_in_projects()

		# Validate that 'Reason for Rejection' is not filled if the status is 'Approved'
		if self.workflow_state == "Approved" and self.reason_for_rejection:
			frappe.throw(title="Approval Error", msg="You cannot approve this request if 'Reason for Rejection' is filled.")
		if self.workflow_state == "Approved" and self.project:
			self.update_project_allocated_resources()
			update_allocated_field(self)
		# Validate that "Reason for Rejection" is filled if the status is "Rejected"
		if self.workflow_state == "Rejected" and not self.reason_for_rejection:
			frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

	def validate_employee_before_approvel(self):
		"""Validate employee field in Required Employees before approving Technical Request"""
		if not self.required_employees:
			frappe.throw(
				_("Please add at least one employee in 'Required Employees' before approving."),
				title=_("Missing Employees")
			)

		for row in self.required_employees:
			if not row.employee and not row.hired_personnel:
				frappe.throw(
					_("Employee is missing in row {0} of 'Required Employees'. Please fill it before approving.")
					.format(row.idx),
					title=_("Missing Employees")
				)

	def update_project_allocated_resources(self):
		"""Update the allocated_manpower_details table in Project when a Technical Request is Approved."""
		if not frappe.db.exists('Project', self.project):
			frappe.throw(_("Invalid Project ID: {0}").format(self.project))

		project = frappe.get_doc('Project', self.project)

		allocated_resources = [
			{
				"department": emp.department,
				"designation": emp.designation,
				"employee": emp.employee,
				"assigned_from": get_datetime(emp.required_from) if emp.required_from else None,
				"assigned_to": get_datetime(emp.required_to) if emp.required_to else None,
				"hired_personnel": "",
				"hired_personnel_contact": ""
			}
			for emp in self.get("required_employees", []) if emp.employee
		]

		if allocated_resources:
			project.extend("allocated_manpower_details", allocated_resources)
			project.save(ignore_permissions=True)

	@frappe.whitelist()
	def validate_required_from_and_required_to(self):
		"""
		Validates that required_from and required_to are properly set and checks
		if required_from is not later than required_to.
		"""
		if not self.required_from or not self.required_to:
			return
		# Convert dates to proper date objects
		required_from = getdate(self.required_from)
		required_to = getdate(self.required_to)

		if required_from > required_to:
			frappe.throw(
				msg=_("Required From cannot be after Required To."),
				title=_("Message")
			)

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if getdate(self.posting_date) > getdate(today()):
				frappe.throw(_("Posting Date cannot be set after today's date."))

	@frappe.whitelist()
	def validate_employee_assignment(self):
		"""
		Check if employees required in Technical Request are already
		allocated in the same project (in Project -> Allocated Manpower Details).
		"""
		if not self.project:
			return

		# Get existing allocations from Project's child table
		allocated_rows = frappe.get_all(
			"Allocated Manpower Detail",
			filters={"parent": self.project},
			fields=["employee", "assigned_from", "assigned_to"]
		)

		for row in self.required_employees:
			if not row.employee:
				continue

			for alloc in allocated_rows:
				if alloc.employee != row.employee:
					continue

				# Check overlapping date ranges
				if (
					(alloc.assigned_from <= row.required_to)
					and (alloc.assigned_to >= row.required_from)
				):
					employee_name = frappe.get_value(
						"Employee", row.employee, "employee_name"
					)
					frappe.throw(
						f"Employee {employee_name} ({row.employee}) is already allocated "
						f"in Project {self.project} during the same time period "
						f"({alloc.assigned_from} to {alloc.assigned_to})."
					)

	@frappe.whitelist()
	def validate_employee_assignment_in_projects(self):
		"""
		Validate that an employee is not assigned to multiple projects
		during the same time period.
		"""
		if not self.project:
			return

		# Get allocated manpower for all projects
		allocated_rows = frappe.get_all(
			"Allocated Manpower Detail",
			fields=["parent", "employee", "assigned_from", "assigned_to"]
		)

		for row in self.required_employees:
			if not row.employee:
				continue

			for alloc in allocated_rows:
				# Skip if same project
				if alloc.parent == self.project:
					continue

				if alloc.employee != row.employee:
					continue

				# Check overlapping dates
				if (alloc.assigned_from <= row.required_to) and (alloc.assigned_to >= row.required_from):
					employee_name = frappe.get_value("Employee", row.employee, "employee_name")
					frappe.throw(
						f"Employee {employee_name} ({row.employee}) is already allocated "
						f"in Project {alloc.parent} during the same time period "
						f"({alloc.assigned_from} to {alloc.assigned_to})."
					)

@frappe.whitelist()
def create_external_resource_request(technical_request):
	tech_req = frappe.get_doc("Technical Request", technical_request)

	# Create new External Resource Request
	external_req = frappe.get_doc({
		"doctype": "External Resource Request",
		"project": tech_req.project,
		"bureau": tech_req.bureau,
		"location": tech_req.location,
		"posting_date": tech_req.posting_date,
		"required_from": tech_req.required_from,
		"required_to": tech_req.required_to,
		"required_resources": [],
		"technical_request": tech_req.name
	})

	for emp in tech_req.required_employees:
		if not emp.employee:
			external_req.append("required_resources", {
				"department": emp.department,
				"designation": emp.designation,
				"required_from": emp.required_from,
				"required_to": emp.required_to
			})

	external_req.insert(ignore_permissions=True)
	return external_req.name

@frappe.whitelist()
def update_allocated_field(doc):
	if doc.workflow_state == "Approved" and doc.project:
		project = frappe.get_doc("Project", doc.project)

		# Ensure required tables exist in both doctypes
		if not hasattr(doc, "required_employees") or not hasattr(project, "allocated_manpower_details"):
			frappe.throw("Required tables are missing in the Technical Request or Project doctype.")

		for emp in doc.required_employees:
			if emp.employee:
				for mp in project.allocated_manpower_details:
					if (
						emp.designation == mp.designation
						and emp.required_from == mp.assigned_from
						and emp.required_to == mp.assigned_to
					):
						mp.status = 'Allocated'

		project.save(ignore_permissions=True)
		frappe.msgprint(f"Allocated manpower updated for Project {doc.project}")
