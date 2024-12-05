# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, getdate
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as add_assign

class ShiftSwapRequest(Document):
    def validate(self):
        # Validate future dates
        if getdate(self.shift_start_date) <= getdate(today()):
            frappe.throw('Shift Start Date must be a future date.')
        if getdate(self.shift_end_date) <= getdate(today()):
            frappe.throw('Shift End Date must be a future date.')

        # Validate shift assignments
        if not self.has_valid_shift_assignment():
            frappe.throw(f'Employee {self.employee} does not have a valid shift assignment in the given date range.')
        if not self.has_valid_shift_assignment(swap=1):
            frappe.throw(f'Swap With Employee {self.swap_with_employee} does not have a valid shift assignment in the given date range.')

        # Validate department
        employee_department = frappe.db.get_value('Employee', self.employee, 'department')
        swap_employee_department = frappe.db.get_value('Employee', self.swap_with_employee, 'department')

        if employee_department != swap_employee_department:
            frappe.throw(
                f'Employee {self.employee} and Swap With Employee {self.swap_with_employee} must belong to the same department.'
            )

    def has_valid_shift_assignment(self, swap=0):
        '''
        Check if the given employee has a valid shift assignment within the specified date range.
        '''
        employee = self.employee if not swap else self.swap_with_employee
        return frappe.db.exists(
            'Shift Assignment',
            {
                'employee': employee,
                'start_date': ['<=', self.shift_end_date],
                'end_date': ['>=', self.shift_start_date],
            }
        )

    def on_update_after_submit(self):
        '''
        Triggered after the Shift Swap Request is updated.
        Initiates the shift swap if the workflow state is "Approved".
        '''
        if self.workflow_state == "Approved" and self.get_db_value("workflow_state") == "Pending Approval":
            self.swap_shifts()

    def swap_shifts(self):
        '''
        Swaps shifts between two employees by:
        1. Cancelling existing shifts for both employees.
        2. Creating new shift assignments with swapped details.
        '''
        employee_shift = frappe.get_all(
            "Shift Assignment",
            filters={
                "employee": self.employee,
                "start_date": ["<=", self.shift_start_date],
                "end_date": [">=", self.shift_end_date],
                "docstatus": 1
            },
            fields=["name", "shift_type","roster_type"]
        )

        swap_with_shift = frappe.get_all(
            "Shift Assignment",
            filters={
                "employee": self.swap_with_employee,
                "start_date":["<=", self.shift_start_date],
                "end_date": [">=", self.shift_end_date],
                "docstatus": 1
            },
            fields=["name", "shift_type","roster_type"]
        )

        for shift in employee_shift:
            shift_doc = frappe.get_doc("Shift Assignment", shift["name"])
            shift_doc.cancel()

        for shift in swap_with_shift:
            shift_doc = frappe.get_doc("Shift Assignment", shift["name"])
            shift_doc.cancel()

        if employee_shift:
            new_shift = frappe.new_doc("Shift Assignment")
            new_shift.update({
                "employee": self.swap_with_employee,
                "shift_type": employee_shift[0]["shift_type"],
                "roster_type": employee_shift[0]["roster_type"],
                "start_date": self.shift_start_date,
                "end_date": self.shift_end_date,
                "status": "Active"
            })
            new_shift.insert(ignore_permissions=True)
            new_shift.submit()

        if swap_with_shift:
            new_shift = frappe.new_doc("Shift Assignment")
            new_shift.update({
                "employee": self.employee,
                "shift_type": swap_with_shift[0]["shift_type"],
                "roster_type": swap_with_shift[0]["roster_type"],
                "start_date": self.shift_start_date,
                "end_date": self.shift_end_date,
                "status": "Active"
            })
            new_shift.insert(ignore_permissions=True)
            new_shift.submit()
