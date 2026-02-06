# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class BudgetTemplate(Document):

	def validate(self):
		self.validate_account_per_cost_center()

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


def validate_account_per_cost_center(self):
	"""
	Validates that there are no duplicate Cost Heads within the same Budget Template and
	no duplicate Account Heads across different Budget Templates for the same Cost Center.
   """

	if not self.cost_center or not self.budget_template_items:
		return

	seen_cost_heads = set()

	for row in self.budget_template_items:
		# Duplicate Cost Head in same Template
		if row.cost_head:
			if row.cost_head in seen_cost_heads:
				frappe.throw(
					_("Duplicate Cost Head <b>{0}</b> is not allowed in the same Budget Template.")
					.format(row.cost_head),
					title=_("Duplicate Cost Head"),
				)
			seen_cost_heads.add(row.cost_head)

		# Duplicate Account across Templates (same Cost Center)
		if not row.account_head:
			continue

		duplicates = frappe.get_all(
			"Budget Template Item",
			filters={
				"account_head": row.account_head,
				"parenttype": "Budget Template",
				"parent": ["!=", self.name],
			},
			fields=["parent"],
			limit=1,
		)

		if not duplicates:
			continue

		template = duplicates[0].parent

		template_cost_center = frappe.db.get_value(
			"Budget Template", template, "cost_center"
		)

		if template_cost_center != self.cost_center:
			continue

		template_link = frappe.utils.get_link_to_form(
			"Budget Template", template
		)

		frappe.throw(
			_(
				"Account : <b>{0}</b> is used in the {1} Budget Template "
				"with the same Cost Center : <b>{2}</b>."
			).format(
				row.account_head,
				template_link,
				self.cost_center,
			),
			title=_("Duplicate Account Found"),
		)


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


