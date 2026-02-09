# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class CostHead(Document):
	def validate(self):
		self.validate_no_duplicate_company_account()

	def validate_no_duplicate_company_account(self):
		"""No duplicate rows with same Company and Default Account in this Cost Head."""
		if not getattr(self, "accounts", None):
			return

		seen = set()
		for row in self.accounts:
			if not row.company or not row.default_account:
				continue
			key = (row.company, row.default_account)
			if key in seen:
				print(seen, "set")
				frappe.throw(
					_(
						"Duplicate Company and Account: <b>{0}</b> and <b>{1}</b> are already used in another row."
					).format(row.company, row.default_account),
					title=_("Duplicate Company & Account"),
				)
			seen.add(key)

