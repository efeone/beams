# # Copyright (c) 2025, efeone and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class EmployeeTravelRequest(Document):
    def on_cancel(self):
        # Validate that "Reason for Rejection" is provided if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def before_save(self):
        if not self.requested_by:
            return

        # Fetch the Batta Policy for the employee
        batta_policy = get_batta_policy(self.requested_by)
        if batta_policy:
            self.batta_policy = batta_policy.get("name")

@frappe.whitelist()
def get_batta_policy(requested_by):
    '''
    Fetch the Batta Policy for the employee's designation and return the Batta policy .
    '''
    if not requested_by:
        return

    # Fetch the employee's designation
    employee = frappe.get_doc("Employee", requested_by)
    designation = employee.designation

    # Fetch the Batta Policy for the designation
    batta_policy = frappe.get_all('Batta Policy', filters={'designation': designation}, fields=['name'])

    if batta_policy:
        return batta_policy[0]
    return None

@frappe.whitelist()
def filter_room_criteria(batta_policy_name):
    '''
    Fetch and return the room criteria for the given Batta Policy.
    '''

    # Fetch the Room Criteria based on the parent
    room_criteria_records = frappe.db.get_all('Room Criteria Table', filters={'parent': batta_policy_name}, pluck='room_criteria')
    if room_criteria_records:
        return room_criteria_records
    else:
        return []


@frappe.whitelist()
def filter_mode_of_travel(batta_policy_name):
    '''
    Fetch and return the mode of travel for the given Batta Policy.
    '''

    # Fetch the Room Criteria based on the parent
    mode_of_travel = frappe.db.get_all('Mode of Travel Table', filters={'parent': batta_policy_name}, pluck='mode_of_travel')
    if mode_of_travel:
        return mode_of_travel
    else:
        return []
