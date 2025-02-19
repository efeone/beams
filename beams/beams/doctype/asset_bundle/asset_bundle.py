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

	def after_insert(self):
		self.generate_asset_bundle_qr()

	def generate_asset_bundle_qr(self):
		qr_code = self.get("qr_code")
		if qr_code and frappe.db.exists({"doctype": "File", "file_url": qr_code}):
			return

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
