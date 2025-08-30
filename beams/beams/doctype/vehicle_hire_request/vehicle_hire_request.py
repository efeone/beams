# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _

class VehicleHireRequest(Document):
	def on_submit(self):
		self.generate_external_vehicle_details_from_hire_request()
		if self.transportation_request:
			frappe.db.set_value(
			"Transportation Request",
			self.transportation_request,
			"vehicle_hire_request",
			self.name
			)
		self.update_hired_vehicles_on_submit()

	def on_cancel(self):
		self.update_hired_vehicles_on_cancel()

	def before_save(self):
		self.validate_posting_date()

	def update_hired_vehicles_on_submit(self):
		'''
		On submission of Vehicle Hire Request update the hired vehicles in linked Transportation Request.
		'''
		if not self.transportation_request:
			frappe.throw("Transportation Request is not linked.")

		tr = frappe.get_doc("Transportation Request", self.transportation_request)

		for rv in self.required_vehicles:

			if rv.vehicle_number and not frappe.db.exists("Vehicle", rv.vehicle_number):
				vehicle_doc = frappe.get_doc({
					"doctype": "Vehicle",
					"vehicle_number": rv.vehicle_number,
					"license_plate": rv.vehicle_number,
					"vehicle_type": rv.vehicle_type,
				})
				vehicle_doc.insert(ignore_permissions=True, ignore_mandatory=True)

			tr.append("vehicles", {
				"hired_vehicle": rv.vehicle_number,
				"from_location": rv.get("from"),
				"to_location": rv.get("to"),
				"no_of_travellers": rv.no_of_travellers,
				"status": "Hired"
			})

		tr.save(ignore_permissions=True)
		frappe.msgprint(f"Vehicles updated in Transportation Request {tr.name}")

	def update_hired_vehicles_on_cancel(self):
		'''
		On cancellation of Transportation Request reset the number of hired vehicles.
		'''
		if self.transportation_request:
			frappe.db.set_value(
				"Transportation Request",
				self.transportation_request,
				"no_of_hired_vehicles",
				0
			)

	def generate_external_vehicle_details_from_hire_request(self):
		'''
		Generate External Vehicle Details records from the Vehicle Hire Request child table
		'''
		project = frappe.get_doc("Project", self.project)

		for vehicle in self.required_vehicles:
			external_vehicle_detail = frappe.new_doc("External Vehicle Details")

			external_vehicle_detail.project = self.project
			external_vehicle_detail.transportation_request = self.transportation_request
			external_vehicle_detail.required_on = self.required_on
			external_vehicle_detail.required_to = self.required_on
			external_vehicle_detail.vehicle_no = vehicle.vehicle_number
			external_vehicle_detail.returned = "No"
			external_vehicle_detail.purpose = f"Vehicle Hire Request Against {self.project}"
			external_vehicle_detail.vehicle_type = vehicle.vehicle_type
			external_vehicle_detail.set("from", vehicle.get("from"))
			external_vehicle_detail.to = vehicle.to
			external_vehicle_detail.vehicle_number = vehicle.vehicle_number

			external_vehicle_detail.save()

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if self.posting_date > today():
				frappe.throw(_("Posting Date cannot be set after today's date."))
