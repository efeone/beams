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
        self.update_vehicle_details_on_project()

    def on_cancel(self):
        self.update_hired_vehicles_on_cancel()

    def before_save(self):
        self.validate_posting_date()

    def update_hired_vehicles_on_submit(self):
        '''
        Calculate the total number of vehicles from the required_vehicles child table
        and update the linked Transportation Request.
        '''
        if self.required_vehicles:
            # Calculate the total number of vehicles
            total_vehicles = len(self.required_vehicles)

            # Update the Transportation Request
            if self.transportation_request:
                frappe.db.set_value(
                    "Transportation Request",
                    self.transportation_request,
                    "no_of_hired_vehicles",
                    total_vehicles
                )

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

    def update_vehicle_details_on_project(self):

        if self.required_vehicles:

            project_details = frappe.get_doc("Project", self.project)

            for vehicle in self.required_vehicles:
                project_details.append("allocated_vehicle_details", {
                    "vehicle": vehicle.vehicle_number,
                    "hired_vehicle": vehicle.get("hired_vehicle", ""),
                    "reference_doctype": "Vehicle Hire Request",
                    "reference_name": self.name,
                    "from":vehicle.get("from"),
                    "to":vehicle.to,
                    "no_of_travellers":vehicle.no_of_travellers,
                    "status":"Hired"
                })
                project_details.save(ignore_permissions=True)

    def generate_external_vehicle_details_from_hire_request(self):
        """
        Generate External Vehicle Details records from the Vehicle Hire Request child table
        """

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
