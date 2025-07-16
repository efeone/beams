# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InwardPass(Document):
	pass

@frappe.whitelist()
def bundle_asset_fetch(names):
    """
    Fetches assets and processed bundles recursively from given asset bundle names
    """
    names = json.loads(names)
    assets = set()
    processed_bundles = set()

    def get_assets_recursive(bundle_name):
        if bundle_name in processed_bundles:
            return
        processed_bundles.add(bundle_name)

        if not frappe.db.exists("Asset Bundle", bundle_name):
            frappe.throw(f"Asset Bundle '{bundle_name}' not found during processing.")

        asset_bundle = frappe.get_doc("Asset Bundle", bundle_name)
        assets.update(asset_bundle.assets)

        for sub_bundle in asset_bundle.bundles:
            get_assets_recursive(sub_bundle.asset_bundle)

    for name in names:
        if not frappe.db.exists("Asset Bundle", name):
            frappe.throw(f"Asset Bundle '{name}' not found. Please check the name.")
        get_assets_recursive(name)

    return list(assets), list(processed_bundles)
