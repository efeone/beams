# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate,format_date
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today

class TechnicalRequest(Document):
    def before_save(self):
        self.validate_posting_date()

    def on_cancel(self):
        # Validate that "Reason for Rejection" is filled if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def validate(self):
        self.validate_required_from_and_required_to()

    @frappe.whitelist()
    def validate_required_from_and_required_to(self):
        """
        Validates that required_from and required_to are properly set and checks
        if required_from is not later than required_to.
        """
        if not self.required_from or not self.required_to:
            return
        # Convert dates to proper date objects
        required_from = getdate(self.required_from)
        required_to = getdate(self.required_to)

        if required_from > required_to:
            frappe.throw(
                msg=_("Required From cannot be after Required To."),
                title=_("Message")
            )
            
    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))


@frappe.whitelist()
def map_external_resource_request(technical_request):
    """
    Map Technical Request to External Resource Request and manually add a child table row.
    """
    mapped_doc = get_mapped_doc(
        "Technical Request",
        technical_request,
        {
            "Technical Request": {
                "doctype": "External Resource Request",
                "field_map": {
                    "name": "technical_request",
                    "project": "project",
                    "bureau": "bureau",
                    "designation": "designation",
                    "required_from": "required_from",
                    "required_to": "required_to"
                }
            }
        }
    )

    mapped_doc.append("required_resources", {
        "designation": mapped_doc.designation,
        "required_from": mapped_doc.required_from,
        "required_to": mapped_doc.required_to
        })

    new_doc = frappe.get_doc(mapped_doc)
    new_doc.insert(ignore_permissions=True)

    return new_doc.name
