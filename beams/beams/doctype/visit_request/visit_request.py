# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _  # Needed for translation
from frappe.utils import today  # Needed to use today()

class VisitRequest(Document):

    @frappe.whitelist()
    def validate_request_date(self):
        '''
        Validates the request_date field of the current document.
        This function checks if request_date is not in the future.
        If the provided date is later than today's date, it raises a validation error.
        '''
        if self.request_date:
            if self.request_date > today():
                frappe.throw(_("Request Date cannot be set after today's date."))
