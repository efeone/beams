# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url_to_form, today


class EmployeeTravelRequest(Document):
    def on_cancel(self):
        # Validate that "Reason for Rejection" is provided if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def validate(self):
        self.validate_dates()
        self.validate_expected_time()
        self.total_days_calculate()

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

    def on_update_after_submit(self):
        # Trigger only when state becomes Approved
        if self.workflow_state != "Approved":
            return

        # Validation: Rejection reason must be empty when approved
        if self.reason_for_rejection:
            frappe.throw(title="Approval Error", msg="You cannot approve this request if 'Reason for Rejection' is filled.")

        if self.is_vehicle_required:
            if not self.travel_vehicle_allocation:
                frappe.throw(title="Approval Error", msg="Vehicle allocation is required before final approval.")

            has_complete_allocation = False
            for allocation in self.travel_vehicle_allocation:
                if allocation.vehicle and allocation.driver:
                    has_complete_allocation = True
                    break

            if not has_complete_allocation:
                frappe.throw(title="Approval Error",
                            msg="You must allocate driver and vehicle before final approval.")


        if not self.mark_attendance:
            return

        employees = []

        # Add main employee
        if self.requested_by:
            employees.append(self.requested_by)

        # Add employees from child table
        for row in self.travellers:
            if row.employee:
                employees.append(row.employee)

        # Remove duplicates and empty entries
        employees = list(set(filter(None, employees)))

        for emp in employees:
            if emp == self.requested_by:
                attendance = frappe.get_doc({
                    "doctype": "Attendance Request",
                    "employee": emp,
                    "from_date": self.start_date,
                    "to_date": self.end_date,
                    "request_type": "On Duty",
                    "company": frappe.db.get_value("Employee", emp, "company"),
                    "description": f"From Travel Request {self.name}",
                    "reason": "On Duty"
                })
                attendance.insert(ignore_permissions=True)
                frappe.msgprint(f"Attendance Request created for {emp}", alert=True, indicator='green')
                continue

            overlapping = frappe.db.exists(
                "Attendance Request",
                {
                    "employee": emp,
                    "from_date": ["<=", self.end_date],
                    "to_date": [">=", self.start_date],
                    "docstatus": ["!=", 2]
                }
            )

            if overlapping:
                continue

            attendance = frappe.get_doc({
                "doctype": "Attendance Request",
                "employee": emp,
                "from_date": self.start_date,
                "to_date": self.end_date,
                "request_type": "On Duty",
                "company": frappe.db.get_value("Employee", emp, "company"),
                "description": f"From Travel Request {self.name}",
                "reason": "On Duty"
            })

            attendance.insert(ignore_permissions=True)
            frappe.msgprint(f"Attendance Request created for {emp}", alert=True, indicator='green')

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))

    @frappe.whitelist()
    def validate_expected_time(self):
        """Ensure Expected Check-out Time is not earlier than Expected Check-in Time."""
        if self.expected_check_in_time and self.expected_check_out_time:
            if self.expected_check_out_time < self.expected_check_in_time:
                frappe.throw("Expected Check-out Time cannot be earlier than Expected Check-in Time.")
    @frappe.whitelist()
    def total_days_calculate(self):
        """Calculate the total number of travel days, ensuring at least one day."""
        if self.start_date and self.end_date:
            start_date = self.start_date if isinstance(self.start_date, datetime) else datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
            end_date = self.end_date if isinstance(self.end_date, datetime) else datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")

            self.total_days = 1 if start_date.date() == end_date.date() else (end_date.date() - start_date.date()).days + 1


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

@frappe.whitelist()
def create_expense_claim(employee, travel_request, expenses):
    '''
    Create an Expense Claim from Travel Request.
    '''

    if isinstance(expenses, str):
        expenses = json.loads(expenses)

    if not expenses:
        frappe.throw(_("Please provide at least one expense item."))

    travel_doc = frappe.get_doc("Employee Travel Request", travel_request)

    expense_claim = frappe.new_doc("Expense Claim")
    expense_claim.travel_request = travel_request
    expense_claim.employee = employee
    expense_claim.approval_status = "Draft"
    expense_claim.posting_date = today()

    # Get Company and payable account
    employee_doc = frappe.get_doc("Employee", employee)
    company = employee_doc.company

    default_payable_account = frappe.get_cached_value('Company', company, 'default_payable_account')
    if not default_payable_account:
        default_payable_account = frappe.db.get_value("Account", {
            "company": company,
            "account_type": "Payable",
            "is_group": 0
        }, "name")

    if not default_payable_account:
        frappe.throw(_("Please set a Default Payable Account in Company {0}").format(company))

    expense_claim.payable_account = default_payable_account

    for expense in expenses:
        amount = expense.get("amount")
        if amount in [None, ""]:
            frappe.throw(_("Expense Amount is required for all items."))

        expense_entry = {
            "amount": amount,
            "expense_date": expense.get("expense_date"),
            "expense_type": expense.get("expense_type"),
            "description": expense.get("description")
        }
        expense_claim.append("expenses", expense_entry)

    expense_claim.total_claimed_amount = sum((item.amount or 0) for item in expense_claim.expenses)
    expense_claim.save()

    frappe.msgprint(
        _('Expense Claim Created: <a href="{0}">{1}</a>').format(get_url_to_form("Expense Claim", expense_claim.name), expense_claim.name),
        alert=True,indicator='green')

    return expense_claim.name
