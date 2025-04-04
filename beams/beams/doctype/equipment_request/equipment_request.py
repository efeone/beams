# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate,now_datetime
from frappe.model.mapper import get_mapped_doc
from frappe import _
from datetime import datetime

class EquipmentRequest(Document):
    def on_update_after_submit(self):
        # Validate that 'Reason for Rejection' is not filled if the status is 'Approved'
        if self.workflow_state == "Approved" and self.reason_for_rejection:
            frappe.throw(title="Approval Error", msg="You cannot approve this request if 'Reason for Rejection' is filled.")

        if self.workflow_state == 'Approved':
            required_from = (
                self.required_from.date()
                if isinstance(self.required_from, datetime)
                else getdate(self.required_from)
            )
            if required_from and self.posting_date and required_from > getdate(self.posting_date):
                if not frappe.db.exists("Asset Reservation Log", {"equipment_request": self.name}):
                    asset_reservation_log = frappe.new_doc("Asset Reservation Log")

                    # Mapping required fields only
                    asset_reservation_log.project = self.project
                    asset_reservation_log.posting_date = self.posting_date
                    asset_reservation_log.location = self.location
                    asset_reservation_log.priority = self.priority
                    asset_reservation_log.reservation_from = self.required_from
                    asset_reservation_log.reservation_to = self.required_to
                    asset_reservation_log.equipment_request = self.name

                    required_items = []

                    for item in self.required_equipments:
                        required_items.append(item.required_item)

                    asset_reservation_log.item = ", ".join(required_items)
                    asset_reservation_log.insert(ignore_permissions=True, ignore_mandatory=True)
                    frappe.db.commit()
                    frappe.msgprint("Asset Reservation Log Created", alert=True, indicator="green")

    def on_cancel(self):
        # Validate that "Reason for Rejection" is provided if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

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
    Calculates acquired_qty as Required Qty - Issued Qty in the child table.
    Only maps the required_item (item) to the child table.
    '''
    equipment_request = frappe.get_doc("Equipment Request", source_name)

    target_doc = get_mapped_doc(
        "Equipment Request",
        source_name,
        {
            "Equipment Request": {
                "doctype": "Equipment Acquiral Request",
                "field_map": {
                    "name": "equipment_request",
                    "expected_start_date": "required_from",
                    "expected_end_date": "required_to",
                    "bureau": "bureau",
                    "location": "location"
                }
            }
        },
        target_doc
    )

    for item in equipment_request.required_equipments:
        acquired_qty = item.required_quantity - item.issued_quantity
        target_item = target_doc.append("required_items", {
            "item": item.required_item,
            "quantity": acquired_qty
        })

    return target_doc


@frappe.whitelist()
def map_asset_movement(source_name, target_doc=None):
    to_employee = frappe.flags.get("args", {}).get("to_employee", '')
    asset = frappe.flags.get("args", {}).get("asset", '')
    ref_type = frappe.flags.get("args", {}).get("ref_type", '')
    ref_name = frappe.flags.get("args", {}).get("ref_name", '')
    print(ref_type, ref_name)
    asset_movement = get_mapped_doc("Equipment Request", source_name, {
        "Equipment Request": {
            "doctype": "Asset Movement",
            "field_map": {

            }
        }
    }, target_doc)
    asset_movement.purpose = 'Issue'
    asset_movement.append('assets', {
            'asset': asset,
            'to_employee': to_employee
        })
    asset_movement.reference_doctype = ref_type
    asset_movement.reference_name = ref_name
    asset_movement.flags.ignore_mandatory = True
    asset_movement.save(ignore_permissions=True)
    return asset_movement
