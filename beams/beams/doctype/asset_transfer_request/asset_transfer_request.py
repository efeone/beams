# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe import _
from frappe.utils import now_datetime, get_url_to_form


class AssetTransferRequest(Document):
    def before_save(self):
        self.validate_posting_date()

    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))
                
@frappe.whitelist()
def get_stock_items_from_bundle(bundle):
    stock_items = frappe.get_all(
        "Asset Bundle Stock Item",
        filters={"parent": bundle},
        fields=["item", "uom", "qty"]
    )
    return stock_items


@frappe.whitelist()
def get_bundle_assets(bundle):
    if not bundle:
        return {"assets": [], "bundles": []}

    bundle_doc = frappe.get_doc("Asset Bundle", bundle)
    assets_list = bundle_doc.assets if bundle_doc.assets else []
    bundles_list = bundle_doc.bundles if bundle_doc.bundles else []

    return {"assets": assets_list, "bundles": bundles_list}


@frappe.whitelist()
def get_asset_return_checklist_template(template_name):
    if not frappe.db.exists("Asset Return Checklist Template", template_name):
        frappe.msgprint(_("Asset Return Checklist Template '{}' not found").format(template_name))

    return frappe.get_all(
        "Asset Return Check",
        filters={"parent": template_name},
        fields=["checklist_item"]
    )
