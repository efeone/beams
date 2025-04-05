# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today
from frappe import _


class TransportationRequest(Document):
    def before_save(self):
        self.validate_posting_date()

    def on_cancel(self):
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def before_update_after_submit(self):
        self.update_no_of_own_vehicles()

    def on_update_after_submit(self):
        if self.workflow_state == "Approved" and self.reason_for_rejection:
            frappe.throw("You cannot approve this request if 'Reason for Rejection' is filled.", title="Approval Error")

        if self.workflow_state == "Approved":
            if not self.project:
                frappe.throw("Project is required to update allocated vehicles.")

            project_doc = frappe.get_doc("Project", self.project)

            if not self.vehicles:
                return
            project_doc.set("allocated_vehicle_details", [])

            for vehicle in self.vehicles:
                project_doc.append("allocated_vehicle_details", {
                    "vehicle": vehicle.vehicle,
                    "hired_vehicle": vehicle.get("hired_vehicle", ""),
                    "reference_doctype": "Transportation Request",
                    "reference_name": self.name,
                    "from":vehicle.from_location,
                    "to":vehicle.to_location,
                    "no_of_travellers":vehicle.no_of_travellers,
                    "allocated":1
                })
            project_doc.save(ignore_permissions=True)

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
            if self.posting_date > today():
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
