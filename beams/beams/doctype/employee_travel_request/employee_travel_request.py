# # Copyright (c) 2025, efeone and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, today,getdate
import json
from frappe.utils import get_url_to_form
from frappe.utils import today
from frappe import _



class EmployeeTravelRequest(Document):
    def on_cancel(self):
        # Validate that "Reason for Rejection" is provided if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def validate(self):
        self.validate_dates()
        self.calculate_total_days()

    def before_save(self):
        self.validate_posting_date()
        if not self.requested_by:
            return

        # Fetch the Batta Policy for the employee
        batta_policy = get_batta_policy(self.requested_by)
        if batta_policy:
            self.batta_policy = batta_policy.get("name")

    @frappe.whitelist()
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                frappe.throw("End Date cannot be earlier than Start Date.")
                if self.start_date < today():
                    frappe.throw("Start Date cannot be in the past.")

    def calculate_total_days(self):
        if self.start_date and self.end_date:
            self.total_days = date_diff(self.end_date, self.start_date)

    def on_update_after_submit(self):
        """
        Create an Attendance Regularization record in 'Draft' when mark_attendance is checked.
        """
        if self.mark_attendance == 1 and self.workflow_state == "Approved":
                attn_reg = frappe.new_doc("Attendance Request")
                attn_reg.employee = self.requested_by
                attn_reg.reason = "On Duty"
                attn_reg.from_date = self.start_date
                attn_reg.to_date = self.end_date
                attn_reg.explanation = "From Travel Request: {}".format(self.name)
                attn_reg.insert()
                self.db_set("attendance_request", attn_reg.name)
                frappe.msgprint(
                    'Attendance Request Created: <a href="{0}">{1}</a>'.format(
                        get_url_to_form(attn_reg.doctype, attn_reg.name), attn_reg.name
                    ),
                    alert=True, indicator="green"
                )

        # Validate that 'Reason for Rejection' is not filled if the status is 'Approved'
        if self.workflow_state == "Approved" and self.reason_for_rejection:
            frappe.throw(title="Approval Error", msg="You cannot approve this request if 'Reason for Rejection' is filled.")

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))

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
    if  batta_policy_name:
        room_criteria_records = frappe.db.get_all('Room Criteria Table', filters={'parent': batta_policy_name}, pluck='room_criteria')
        if room_criteria_records:
            return room_criteria_records
        else:
            return []
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
