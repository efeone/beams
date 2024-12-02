# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class ProvidentFund(Document):
    def validate(self):
        self.check_existing_provident_fund()

    def check_existing_provident_fund(self):
        '''
        Checks if a Provident Fund record already exists for the employee.
        If it exists raises an error to prevent duplication.
        '''
        if not self.employee_name:
            frappe.throw(_("Employee Name is required"))

        existing_record = frappe.db.get_value(
            "Provident Fund",
            {"employee_name": self.employee_name, "name": ["!=", self.name]},
            "name"
        )

        if existing_record:
            frappe.throw(_("A Provident Fund record already exists for this employee."))
