# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class OutwardPass(Document):
	
	def validate(self):
		"""Run validations before saving the document."""
		self.validate_reason_for_rejection()

	def validate_reason_for_rejection(self):
		"""
		Ensure that a Reason for Rejection is provided
		whenever the workflow state is set to 'Rejected'.
		"""
		if self.workflow_state == "Rejected" and not self.reason_for_rejection:
			frappe.throw(
				msg="Please provide a Reason for Rejection before rejecting this request.",
				title="Missing Reason for Rejection"
			)

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
