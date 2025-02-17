# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetBundle(Document):
	def before_save(self):
		if not(self.assets or self.bundles or self.stock_items):
			frappe.throw("At least one of Stock Items, Assets, or Bundles must be filled in.")
