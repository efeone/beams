# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document


class VisitorPass(Document):

    def validate(self):
        self.validate_issued_date_and_expire_on()
        self.validate_issued_date_and_returned_date()
        self.validate_returned_date_and_returned_time()


    def validate_returned_date_and_returned_time(self):
            '''
                Ensure  Returned Date and Time selection based on workflow state
            '''
            if self.workflow_state == 'Issued':
                if not self.returned_date or not self.returned_time:
                    frappe.throw(_('Please select an Returned Date and Time.'))

    @frappe.whitelist()
    def validate_issued_date_and_expire_on(self):
        """
        Validates that issued_date and expire_on are properly set and checks
        if issued_date is not later than expire_on.
        """
        if not self.issued_date or not self.expire_on:
            return
        # Convert dates to proper date objects
        issued_date = getdate(self.issued_date)
        expire_on = getdate(self.expire_on)

        if issued_date > expire_on:
            frappe.throw(
                msg=_("Issued Date cannot be after Expire On."),
                title=_("Message")
            )
    @frappe.whitelist()
    def validate_issued_date_and_returned_date(self):
        """
        Validates that issued_date and returned_date are properly set and checks
        if issued_date is not later than returned_date.
        """
        if not self.issued_date or not self.returned_date:
            return
        # Convert dates to proper date objects
        issued_date = getdate(self.issued_date)
        returned_date = getdate(self.returned_date)

        if issued_date > returned_date:
            frappe.throw(
                msg=_("Issued Date cannot be after Returned Date."),
                title=_("Message")
            )
