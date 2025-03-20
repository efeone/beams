# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate
from frappe import _
from frappe.utils import today
from frappe.utils import get_datetime

class ExternalResourceRequest(Document):

    def validate(self):
        self.validate_required_from_and_required_to()

    def before_save(self):
        self.validate_posting_date()

    def on_submit(self):
        self.update_external_resources_project_allocated_resources()

    def update_external_resources_project_allocated_resources(self):
        """Update the allocated_resources_details table in Project when a External Resource Request is Submitted."""
        if not frappe.db.exists('Project', self.project):
            frappe.throw(_("Invalid Project ID: {0}").format(self.project))

        project = frappe.get_doc('Project', self.project)

        allocated_resources = [
            {
                "department": req.department,
                "designation": req.designation,
                "assigned_from": get_datetime(req.required_from) if req.required_from else None,
                "assigned_to": get_datetime(req.required_to) if req.required_to else None,
                "hired_personnel": req.hired_personnel,
                "hired_personnel_contact_info": req.contact_number
            }
            for req in self.get("required_resources", [])
        ]

        if allocated_resources:
            project.extend("allocated_resources_details", allocated_resources)
            project.save(ignore_permissions=True)


    @frappe.whitelist()
    def validate_required_from_and_required_to(self):
        """Validates required_from and required_to dates."""
        if not self.required_from or not self.required_to:
            return

        required_from = getdate(self.required_from)
        required_to = getdate(self.required_to)

        if required_from > required_to:
            frappe.throw(
                msg=_('The "Required From" date cannot be after the "Required To" date.'),
                title=_('Validation Error')
            )

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            posting_date = getdate(self.posting_date)
            today_date = getdate(today())
            if posting_date > today_date:
                frappe.throw(_("Posting Date cannot be set after today's date."))


    @frappe.whitelist()
    def updated_required_resources(self):
        for req in self.required_resources:
            req.required_from = self.required_from
            req.required_to = self.required_to
