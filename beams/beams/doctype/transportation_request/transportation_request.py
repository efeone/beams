# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today, getdate
from frappe import _

class TransportationRequest(Document):
	def before_save(self):
		self.validate_posting_date()

	def validate(self):
		if self.workflow_state == "Rejected" and not self.reason_for_rejection:
			frappe.throw("Please provide a Reason for Rejection before rejecting this request.")
		self.update_vehicle_counts()
		if self.workflow_state == "Approved":
			self.validate_vehicle_before_approvel()

	def validate_vehicle_before_approvel(self):
		"""Validate vehicle allocation before approving Transportation Request"""

		if not self.vehicles:
			frappe.throw(
				_("Please add at least one vehicle in 'vehicles' before approving."),
				title=_("Missing Vehicle")
			)

		for row in self.vehicles:
			if not row.vehicle and not row.hired_vehicle:
				frappe.throw(
					_("Vehicle is missing in row {0} of 'Vehicles'. Please fill it before approving.")
					.format(row.idx),
					title=_("Missing Vehicle")
				)

		required_count = len(self.required_vehicle or [])
		allocated_count = len(self.vehicles or [])

		if required_count and allocated_count < required_count:
			frappe.throw(
				_("You need to allocate {0} vehicles, but only {1} are added.")
				.format(required_count, allocated_count),
				title=_("Insufficient Vehicles")
			)

	def before_update_after_submit(self):
		self.update_vehicle_counts()

	def on_submit(self):

		self.update_vehicle_counts()

		if self.workflow_state == "Approved" and self.reason_for_rejection:
			frappe.throw("You cannot approve this request if 'Reason for Rejection' is filled.", title="Approval Error")

		if self.workflow_state == "Approved":
			if not self.project:
				frappe.throw("Project is required to update allocated vehicles.")
			for vehicle in self.vehicles:
				if not vehicle.status:
					vehicle.status = "Allocated"

			project_doc = frappe.get_doc("Project", self.project)

			if not self.vehicles:
				return

			existing_vehicles = project_doc.get("allocated_vehicle_details", [])

			vehicles_to_update = {(v.vehicle or v.hired_vehicle): v for v in self.vehicles}

			updated_vehicle_details = []

			for existing_vehicle in existing_vehicles:
				vehicle_key = existing_vehicle.get("vehicle") or existing_vehicle.get("hired_vehicle")

				if (existing_vehicle.get("reference_name") == self.name and
					vehicle_key in vehicles_to_update):

					vehicle = vehicles_to_update[vehicle_key]

					updated_vehicle_details.append({
						"vehicle": vehicle.vehicle or "",
						"hired_vehicle": vehicle.get("hired_vehicle", ""),
						"reference_doctype": "Transportation Request",
						"reference_name": self.name,
						"from": vehicle.from_location,
						"to": vehicle.to_location,
						"no_of_travellers": vehicle.no_of_travellers,
						"status": vehicle.status
					})

					del vehicles_to_update[vehicle_key]
				else:
					updated_vehicle_details.append(existing_vehicle)

			for v in vehicles_to_update.values():
				updated_vehicle_details.append({
					"vehicle": v.vehicle or "",
					"hired_vehicle": v.get("hired_vehicle", ""),
					"reference_doctype": "Transportation Request",
					"reference_name": self.name,
					"from": v.from_location,
					"to": v.to_location,
					"no_of_travellers": v.no_of_travellers,
					"status": v.status
				})

			project_doc.set("allocated_vehicle_details", updated_vehicle_details)

			try:
				project_doc.save(ignore_permissions=True)
				frappe.msgprint(f"Vehicles are updated for Project {self.project}")
			except Exception as e:
				frappe.throw(f"Failed to update Project: {str(e)}")

	def update_vehicle_counts(self):
		'''
		Calculate:
		- Total number of vehicles (rows in Vehicles table) → No. of Own Vehicles
		- Total number of hired vehicles (rows where hired_vehicle is checked/Yes) → No. of Hired Vehicles
		'''
		total_vehicles = len(self.vehicles or [])
		hired_vehicles = sum(1 for row in (self.vehicles or []) if row.hired_vehicle)

		self.no_of_own_vehicles = total_vehicles - hired_vehicles
		self.no_of_hired_vehicles = hired_vehicles

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			posting_date = getdate(self.posting_date)  # Convert to date object
			if posting_date > getdate(today()):
				frappe.throw(_("Posting Date cannot be set after today's date."))

@frappe.whitelist()
def map_transportation_to_vehicle(source_name, target_doc=None):
	'''
	Maps fields from the Transportation Request doctype to the Vehicle Hire Request doctype,
	including selected values from the child table if applicable.
	'''
	vehicle_hire_request = get_mapped_doc(
		"Transportation Request",
		source_name,
		{
			"Transportation Request": {
				"doctype": "Vehicle Hire Request",
				"field_map": {
					"project": "project",
					"bureau": "bureau",
					"location": "location",
					"required_on": "required_on"
				}
			}
		},
		target_doc
	)

	return vehicle_hire_request