# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate
from frappe.model.mapper import get_mapped_doc
from frappe import _

class EquipmentRequest(Document):
    def validate(self):
        self.validate_required_from_and_required_to()

    def before_save(self):
        self.validate_posting_date()

    @frappe.whitelist()
    def validate_required_from_and_required_to(self):
        """
        Validates that required_from and required_to are properly set and checks
        if required_from is not later than required_to.
        """
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
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))


@frappe.whitelist()
def map_equipment_acquiral_request(source_name, target_doc=None):
    '''
    Maps fields from the Equipment Request doctype to the Equipment Acquiral Request doctype.
    '''
    return get_mapped_doc(
        "Equipment Request",
        source_name,
        {
            "Equipment Request": {
                "doctype": "Equipment Acquiral Request",
                "field_map": {
                    "name": "equipment_request",
                    "expected_start_date": "required_from",
                    "expected_end_date": "required_to",
                    "bureau": "bureau"
                }
            }
        },
        target_doc
    )
