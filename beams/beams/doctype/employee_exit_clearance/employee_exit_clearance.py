# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeExitClearance(Document):
    def on_submit(self):
        self.update_status()

    def update_status(self):
        '''
        Updates the 'status' field in the Employee Clearance child table of Employee Separation to 'Completed'.

        '''
        # Fetch the latest Employee Separation document for the given employee
        employee_separation = frappe.get_doc("Employee Separation", {"employee": self.employee})
        if not employee_separation:
            frappe.throw(f"No Employee Separation record found for Employee {self.employee}")

        # Iterate through Employee Clearance rows and update the status
        for row in employee_separation.employee_clearance:
            if row.employee_exit_clearance == self.name:
                frappe.db.set_value(
                    "Employee Clearance",
                    row.name,
                    "status",
                    "Completed"
                )

        # Check if all rows in the Employee Clearance table have the status 'Completed'
        all_completed = all(
            frappe.db.get_value("Employee Clearance", r.name, "status") == "Completed"
            for r in employee_separation.employee_clearance
        )

        # If all are completed, update the Employee Separation exit status
        if all_completed:
            frappe.db.set_value(
                "Employee Separation",
                employee_separation.name,
                "employee_exit_status",
                "Completed"
            )
