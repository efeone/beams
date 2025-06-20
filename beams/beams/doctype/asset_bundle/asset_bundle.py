# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
import io
from pyqrcode import create
import json


class AssetBundle(Document):
	def before_save(self):
		if not(self.assets or self.bundles or self.stock_items):
			frappe.throw("At least one of Stock Items, Assets, or Bundles must be filled in.")
		self.generate_asset_bundle_qr()

	def after_insert(self):
		self.generate_asset_bundle_qr_file()


	def generate_asset_bundle_qr_file(self):
		bundle_qr_code = self.get("bundle_qr_code")
		if bundle_qr_code and frappe.db.exists({"doctype": "File", "file_url": bundle_qr_code}):
			return

		doc_url = self.get_si_file()
		qr_image = io.BytesIO()
		url = create(doc_url, error="L")
		url.png(qr_image, scale=4, quiet_zone=1)
		name = frappe.generate_hash(self.name, 5)
		filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
		_file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": filename,
				"is_private": 0,
				"content": qr_image.getvalue(),
				"attached_to_doctype": self.get("doctype"),
				"attached_to_name": self.get("name"),
				"attached_to_field": "bundle_qr_code",
			}
		)
		_file.save()
		self.db_set("bundle_qr_code", _file.file_url)

	def validate(self):
		self.validate_asset_locations()

	def validate_asset_locations(self):
		"""
			Ensure all selected assets are from the same location.
		"""
		if not self.assets:
			return

		locations = set()

		for asset in self.assets:
			asset_doc = frappe.get_doc("Asset", asset.asset)
			if asset_doc.location:
				locations.add(asset_doc.location)

		if len(locations) > 1:
			frappe.throw("Selected assets belong to different locations. Please select assets from the same location.")

	def get_si_file(self):
		return self.name

	def generate_asset_bundle_qr(self):
		doc_url = self.get_si_json()
		qr_image = io.BytesIO()
		url = create(doc_url, error="L")
		url.png(qr_image, scale=4, quiet_zone=1)
		name = frappe.generate_hash(self.name, 5)
		filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
		_file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": filename,
				"is_private": 0,
				"content": qr_image.getvalue(),
				"attached_to_doctype": self.get("doctype"),
				"attached_to_name": self.get("name"),
				"attached_to_field": "qr_code",
			}
		)
		_file.save()
		self.db_set("qr_code", _file.file_url)

	def get_si_json(self):
	    essential_fields = {"assets": "asset", "bundles": "asset_bundle", "stock_items": ["item", "uom", "qty"]}
	    item_data = {}
	    for field, keys in essential_fields.items():
	        values = []
	        for row in self.get(field, []):
	            if isinstance(keys, list):
	                values.append({key: getattr(row, key) for key in keys})
	            else:
	                values.append({keys: getattr(row, keys)})
	        item_data[field] = values
	    return json.dumps(item_data, indent=4)

	def on_update(self):
	    """
	    Prevents updating an Asset Bundle if it is currently in a Returned Asset Transfer Request.
	    """
	    non_returned_request_names = frappe.get_all(
	        "Asset Transfer Request",
	        filters={"workflow_state":["!=", "Returned"]},
	        pluck="name"
	    )
	    if not non_returned_request_names:
	        return
	    non_returned_bundles = frappe.get_all(
	        "Bundles",
	        filters={"parent": ["in", non_returned_request_names]},
	        pluck="asset_bundle"
	    )
	    directly_assigned_bundles = frappe.get_all(
	        "Asset Transfer Request",
	        filters={"name": ["in", non_returned_request_names]},
	        pluck="bundle"
	    )
	    non_returned_bundles_set = set(non_returned_bundles) | set(directly_assigned_bundles)
	    if self.name in non_returned_bundles_set:
	        frappe.throw(f"Cannot update Asset Bundle '{self.name}' as it is in a non Returned Asset Transfer Request")


@frappe.whitelist()
def bundle_asset_fetch(names):
    '''
    Fetch assets from specified Asset Bundles, including recursively retrieving assets from nested bundles.
    '''
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

@frappe.whitelist()
def get_selected_assets():
    selected_assets = []
    asset_entries = frappe.get_all("Assets", fields=["asset", "parent"], filters={"parenttype": "Asset Bundle"})

    for entry in asset_entries:
        if entry.asset:
            selected_assets.append(entry.asset)
    return list(set(selected_assets))

@frappe.whitelist()
def get_selected_bundles():
    selected_bundles = set()
    bundle_entries = frappe.get_all("Bundles", fields=["asset_bundle"])

    for entry in bundle_entries:
        selected_bundles.add(entry["asset_bundle"])
    return list(selected_bundles)
