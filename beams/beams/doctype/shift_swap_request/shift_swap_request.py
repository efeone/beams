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
            employee_name = frappe.db.get_value('Employee', self.employee, 'employee_name')
            employee_link = f'<a href="/app/employee/{self.employee}" target="_blank">{employee_name}</a>'
            frappe.throw(f'Employee {employee_link} does not have a valid shift assignment in the given date range.')

        if not self.has_valid_shift_assignment(swap=1):
            swap_employee_name = frappe.db.get_value('Employee', self.swap_with_employee, 'employee_name')
            swap_employee_link = f'<a href="/app/employee/{self.swap_with_employee}" target="_blank">{swap_employee_name}</a>'
            frappe.throw(f'Swap With Employee {swap_employee_link} does not have a valid shift assignment in the given date range.')

        # Validate department
        employee_department = frappe.db.get_value('Employee', self.employee, 'department')
        swap_employee_department = frappe.db.get_value('Employee', self.swap_with_employee, 'department')

        if employee_department != swap_employee_department:
            # Fetch employee names
            employee_name = frappe.db.get_value('Employee', self.employee, 'employee_name')
            swap_employee_name = frappe.db.get_value('Employee', self.swap_with_employee, 'employee_name')

            employee_link = f'<a href="/app/employee/{self.employee}" target="_blank">{employee_name}</a>'
            swap_employee_link = f'<a href="/app/employee/{self.swap_with_employee}" target="_blank">{swap_employee_name}</a>'

            frappe.throw(
                f'Employee {employee_link} and Swap With Employee {swap_employee_link} must belong to the same department.',
                title="Department Mismatch"
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
        if self.workflow_state == "Approved":
            self.swap_shifts()

    def swap_shifts(self):
        '''
        Swaps shifts between two employees by:
        1. Adjusting existing shifts to remove the swapped period.
        2. Creating new shift assignments for the swapped period.
        '''
        employee_shift = frappe.get_all(
            "Shift Assignment",
            filters={
                "employee": self.employee,
                "start_date": ["<=", self.shift_start_date],
                "end_date": [">=", self.shift_end_date],
                "docstatus": 1
            },
            fields=["name", "shift_type", "roster_type", "start_date", "end_date"]
        )

        swap_with_shift = frappe.get_all(
            "Shift Assignment",
            filters={
                "employee": self.swap_with_employee,
                "start_date": ["<=", self.shift_start_date],
                "end_date": [">=", self.shift_end_date],
                "docstatus": 1
            },
            fields=["name", "shift_type", "roster_type", "start_date", "end_date"]
        )

        def adjust_existing_shifts(shift_list, employee):
            '''
            Adjusts shift assignments by:
            - Splitting the original shift into two if necessary.
            - Removing only the swapped portion.
            '''
            for shift in shift_list:
                shift_doc = frappe.get_doc("Shift Assignment", shift["name"])

                # Cancel the shift only if the entire period is covered
                shift_doc.cancel()

                # Create new shifts for the unaffected periods
                if shift["start_date"] < self.shift_start_date:
                    new_shift = frappe.new_doc("Shift Assignment")
                    new_shift.update({
                        "employee": employee,
                        "shift_type": shift["shift_type"],
                        "roster_type": shift["roster_type"],
                        "start_date": shift["start_date"],
                        "end_date": frappe.utils.add_days(self.shift_start_date, -1),
                        "status": "Active"
                    })
                    new_shift.insert(ignore_permissions=True)
                    new_shift.submit()

                if shift["end_date"] > self.shift_end_date:
                    new_shift = frappe.new_doc("Shift Assignment")
                    new_shift.update({
                        "employee": employee,
                        "shift_type": shift["shift_type"],
                        "roster_type": shift["roster_type"],
                        "start_date": frappe.utils.add_days(self.shift_end_date, 1),
                        "end_date": shift["end_date"],
                        "status": "Active"
                    })
                    new_shift.insert(ignore_permissions=True)
                    new_shift.submit()

        # Adjust original shifts for both employees
        adjust_existing_shifts(employee_shift, self.employee)
        adjust_existing_shifts(swap_with_shift, self.swap_with_employee)

        # Create new swapped shift assignments
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
