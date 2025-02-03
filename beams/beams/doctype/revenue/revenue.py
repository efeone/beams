# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Revenue(Document):
	def before_naming(self):
		self.naming_series = f"{{{frappe.scrub(self.revenue_against)}}}./.{self.fiscal_year}/.###"
