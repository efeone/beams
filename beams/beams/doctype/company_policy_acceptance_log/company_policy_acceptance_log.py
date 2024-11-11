# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document


class CompanyPolicyAcceptanceLog(Document):

    def before_submit(self):
        """
        Validate conditions before submitting the document:
        1. Ensure 'Read and Accepted' checkbox is checked.
        2. Ensure 'Digital Sign' field is filled.
        3. Ensure that only the selected employee can submit this document.
        """
        # Ensure 'Read and Accepted' is checked
        if not self.read_and_accepted:
            frappe.throw(_("You must check 'Read and Accepted' before submitting."))

        # Ensure 'Digital Sign' is filled
        if not self.digital_sign:
            frappe.throw(_("You must provide a Digital Signature before submitting."))

        # Fetch the user_id of the selected employee
        employee_user_id = frappe.db.get_value("Employee", self.employee, "user_id")

        # Ensure only the selected employee can submit
        if frappe.session.user != employee_user_id:
            frappe.throw(_("Only the selected employee can submit this document."))
