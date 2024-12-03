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

    def on_update(self):
        """
        Triggered when the document is updated. Creates a ToDo for the HOD if the workflow state is "Pending Approval".
        """
        if self.workflow_state == "Pending Approval":
            self.create_todo_for_hod()

    def create_todo_for_hod(self):
        """
        Create a ToDo task for the HOD of the employee's department when a Shift Swap Request is in "Pending Approval".
        """
        
        department = frappe.db.get_value("Employee", self.employee, "department")
        if not department:
            frappe.msgprint(
                f"No department found for employee {self.employee}.", alert=True
            )
            return

        hod_employee = frappe.db.get_value("Department", department, "head_of_department")
        if not hod_employee:
            frappe.msgprint(
                f"No Head of Department assigned for department {department}.", alert=True
            )
            return

        hod_user = frappe.db.get_value("Employee", hod_employee, "user_id")
        if not hod_user:
            frappe.msgprint(
                f"The Head of Department ({hod_employee}) does not have a linked user ID.",
                alert=True,
            )
            return

        admin_message = (
            f"A new Shift Swap Request ({self.name}) has been created by Employee "
            f"{self.employee}. Please review and take appropriate action."
        )

        try:
            add_assign(
				{
					"assign_to": [hod_user],
					"doctype": "Shift Swap Request",
					"name": self.name,
					"description": admin_message,
				}
			)
            frappe.msgprint(
                f"Task successfully assigned to HOD ({hod_user}) for Shift Swap Request {self.name}.",
                alert=True,
            )
        except Exception as e:
            frappe.log_error(message=f"Failed to create ToDo for HOD: {str(e)}", title="Shift Swap Request")
            frappe.msgprint(
                "An error occurred while assigning the task to the HOD. Please check the logs for more details.",
                alert=True,
            )
