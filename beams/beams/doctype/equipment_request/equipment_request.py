# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate,now_datetime
from frappe.model.mapper import get_mapped_doc
from frappe import _
from datetime import datetime
import json

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
                        if not frappe.db.exists("Item", item.required_item):
                            frappe.throw(f"Item '{item.required_item}' does not exist.")

                        asset_reservation_log = frappe.new_doc("Asset Reservation Log")
                        asset_reservation_log.project = self.project
                        asset_reservation_log.posting_date = self.posting_date
                        asset_reservation_log.location = self.location
                        asset_reservation_log.priority = self.priority
                        asset_reservation_log.reservation_from = self.required_from
                        asset_reservation_log.reservation_to = self.required_to
                        asset_reservation_log.equipment_request = self.name
                        asset_reservation_log.item = item.required_item  # assign only a single item
                        asset_reservation_log.insert(ignore_permissions=True, ignore_mandatory=True)

                    frappe.db.commit()
                    frappe.msgprint("Asset Reservation Logs Created", alert=True, indicator="green")


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
            if getdate(self.posting_date) > getdate(today()):
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
def map_asset_movement(source_name, assigned_to=None, items=None, purpose="Issue", target_doc=None):
    """
    Maps an Equipment Request to an Asset Movement with selected assets and assigns them to an employee.
    Also fills reference_doctype and reference_name.
    Skips items where count is 0 or less.
    """
    if isinstance(items, str):
        items = json.loads(items)

    def postprocess(source, target):
        employee_id = frappe.db.get_value("Employee", {"user_id": assigned_to})
        if not employee_id:
            frappe.throw(f"No Employee linked to User '{assigned_to}'")

        target.to_employee = employee_id
        target.reference_doctype = "Equipment Request"
        target.reference_name = source.name
        target.purpose = purpose or "Issue"

        if items:
            for row in items:
                item_code = row.get("item")
                count = row.get("count")
                reference_name = row.get("name")

                if not item_code or not isinstance(count, (int, float)) or count <= 0:
                    continue

                assets = frappe.get_all(
                    "Asset",
                    filters={
                        "item_code": item_code,
                        "docstatus": 1,
                        "status": "Submitted"
                    },
                    fields=["name", "location"],
                    limit=int(count)
                )

                for asset in assets:
                    target.append("assets", {
                        "asset": asset.name,
                        "source_location": asset.location,
                        "to_employee": employee_id,
                        "target_location": None,
                        "reference_name": reference_name
                    })

    return get_mapped_doc(
        "Equipment Request",
        source_name,
        {
            "Equipment Request": {
                "doctype": "Asset Movement"
            }
        },
        target_doc,
        postprocess
    )
