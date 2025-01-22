# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class TransportationRequest(Document):

    def on_cancel(self):
        # Validate that "Reason for Rejection" is filled if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def before_update_after_submit(self):
        self.update_no_of_own_vehicles()

    def update_no_of_own_vehicles(self):
        '''
        Calculate the total number of rows in the "Vehicles" child table
        and update the "No. of Own Vehicles" field.
        '''
        # Always calculate and update the value regardless of the state
        total_vehicles = len(self.vehicles or [])
        self.no_of_own_vehicles = total_vehicles


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
                    "required_on": "required_on"
                }
            }
        },
        target_doc
    )

    return vehicle_hire_request
