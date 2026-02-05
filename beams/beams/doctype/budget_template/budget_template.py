# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BudgetTemplate(Document):

	def set_default_account(self):
		"""  Set the default account for each budget template item based on the associated cost subhead and company.
		"""
		if not hasattr(self, "budget_template_item") or not self.budget_template_item:
			return

		for item in self.budget_template_item:
			if not item.cost_sub_head or not self.company:
				item.account = ""
				continue

			cost_subhead_doc = frappe.get_doc("Cost Subhead", item.cost_sub_head)

			if cost_subhead_doc.accounts:
				account_found = next((acc for acc in cost_subhead_doc.accounts if acc.company == self.company), None)
				item.account = account_found.default_account if account_found else ""
			else:
				item.account = ""

	def before_save(self):
		self.set_default_account()



@frappe.whitelist()
def get_budget_approver_employees(doctype, txt, searchfield, start, page_len, filters):
	"""  
	Fetch employees with the role of 'Budget Approver' for the current company.
	"""
	users = frappe.get_all(
		"Has Role",
		filters={"role": "Budget Approver"},
		pluck="parent"
	)

	if not users:
		return []

	result = frappe.get_all(
		"Employee",
		filters={
			"user_id": ["in", users]
		},
		fields=["name", "employee_name"],
	)

	return [(row.name, row.employee_name) for row in result]


