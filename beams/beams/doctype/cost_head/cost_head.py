# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class CostHead(Document):
	def validate(self):
		self.validate_duplicate_company()

	def validate_duplicate_company(self):
		"""Allow only one row per Company in this Cost Head."""

		seen_companies = set()

		for row in self.accounts:
			if not row.company:
				continue

			if row.company in seen_companies:
				frappe.throw(
					_("Cannot set multiple Item Defaults for a company."),
					title=_("Duplicate Company"),
				)

			seen_companies.add(row.company)

