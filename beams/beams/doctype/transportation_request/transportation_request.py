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
		self.update_no_of_own_vehicles()

	def before_update_after_submit(self):
		self.update_no_of_own_vehicles()

	def on_submit(self):
		# Always update own vehicles count on workflow update
		self.update_no_of_own_vehicles()

		if self.workflow_state == "Approved" and self.reason_for_rejection:
			frappe.throw("You cannot approve this request if 'Reason for Rejection' is filled.", title="Approval Error")

		if self.workflow_state == "Approved":
			if not self.project:
				frappe.throw("Project is required to update allocated vehicles.")

			project_doc = frappe.get_doc("Project", self.project)

			if not self.vehicles:
				return

			existing_vehicles = project_doc.get("allocated_vehicle_details", [])
			vehicles_to_update = {vehicle.vehicle: vehicle for vehicle in self.vehicles}

			updated_vehicle_details = []
			for existing_vehicle in existing_vehicles:
				if existing_vehicle.reference_name != self.name:
					updated_vehicle_details.append(existing_vehicle)
				elif existing_vehicle.vehicle in vehicles_to_update:
					vehicle = vehicles_to_update[existing_vehicle.vehicle]
					updated_vehicle_details.append({
						"vehicle": vehicle.vehicle,
						"hired_vehicle": vehicle.get("hired_vehicle", ""),
						"reference_doctype": "Transportation Request",
						"reference_name": self.name,
						"from": vehicle.from_location,
						"to": vehicle.to_location,
						"no_of_travellers": vehicle.no_of_travellers,
						"status": "Allocated"
					})
					del vehicles_to_update[existing_vehicle.vehicle]

			for vehicle in vehicles_to_update.values():
				updated_vehicle_details.append({
					"vehicle": vehicle.vehicle,
					"hired_vehicle": vehicle.get("hired_vehicle", ""),
					"reference_doctype": "Transportation Request",
					"reference_name": self.name,
					"from": vehicle.from_location,
					"to": vehicle.to_location,
					"no_of_travellers": vehicle.no_of_travellers,
					"status": "Allocated"
				})

			project_doc.set("allocated_vehicle_details", updated_vehicle_details)

			try:
				project_doc.save(ignore_permissions=True)
			except Exception as e:
				frappe.throw(f"Failed to update Project: {str(e)}")

	def update_no_of_own_vehicles(self):
		'''
		Calculate the total number of rows in the "Vehicles" child table
		and update the "No. of Own Vehicles" field.
		'''
		total_vehicles = len(self.vehicles or [])
		self.no_of_own_vehicles = total_vehicles

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