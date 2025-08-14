# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import getdate, get_datetime_str, get_time
from frappe.model.document import Document


class VisitorPass(Document):

    def validate(self):
        self.validate_issued_date_and_expire_on()
        self.validate_issued_date_and_returned_date()
        self.validate_returned_date_and_returned_time()

    def validate_returned_date_and_returned_time(self):
        '''
        Ensure Returned Date and Time selection based on workflow state
        '''
        if self.workflow_state == 'Issued':
            if not self.returned_date:
                frappe.throw(_('Please select a Returned Date and Time.'))

    @frappe.whitelist()
    def validate_issued_date_and_expire_on(self):
        '''
        Validates that issued_date and expire_on are properly set and checks
        if issued_date is not later than expire_on.
        '''
        if not self.issued_date or not self.expire_on:
            return

        issued_date = getdate(self.issued_date)
        expire_on = getdate(self.expire_on)

        if issued_date > expire_on:
            frappe.throw(
                msg=_("Issued Date cannot be after Expire On."),
                title=_("Validation Error")
            )

    @frappe.whitelist()
    def validate_issued_date_and_returned_date(self):
        '''
        Validates that issued_date and returned_date are properly set and checks
        if issued_date is not later than returned_date.
        Also checks that issued_time is not later than returned_time if both dates are the same.
        '''
        if not self.issued_date or not self.returned_date:
            return

        issued_date = getdate(self.issued_date)
        returned_date = getdate(self.returned_date)

        if issued_date > returned_date:
            frappe.throw(
                msg=_("Issued Date cannot be after Returned Date."),
                title=_("Validation Error")
            )

        if issued_date == returned_date:
            if self.issued_time and self.returned_time:
                issued_time = get_time(self.issued_time)
                returned_time = get_time(self.returned_time)

                if issued_time >= returned_time:
                    frappe.throw(
                        msg=_("Issued Time must be greater than Returned Time "),
                        title=_("Validation Error")
                    )
