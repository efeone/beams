# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class BudgetTemplate(Document):

	def validate(self):
		self.validate_account_per_cost_center()

	def validate_account_per_cost_center(self):
		'''
			Validates that there are no duplicate Cost Heads within the same Budget Template and
			no duplicate Account Heads across different Budget Templates for the same Cost Center.
		'''

		if not self.cost_center or not self.budget_template_items:
			return

		seen_cost_heads = set()

		for row in self.budget_template_items:
			# Duplicate Cost Head in same Template
			if row.cost_head:
				if row.cost_head in seen_cost_heads:
					frappe.throw(
						_('Duplicate Cost Head <b>{0}</b> is not allowed in the same Budget Template.')
						.format(row.cost_head),
						title=_('Duplicate Cost Head'),
					)
				seen_cost_heads.add(row.cost_head)

			# Duplicate Account across Templates (same Cost Center)
			if not row.account_head:
				continue

			duplicates = frappe.get_all(
				'Budget Template Item',
				filters={
					'account_head': row.account_head,
					'parenttype': 'Budget Template',
					'parentfield': 'budget_template_items',
					'parent': ['!=', self.name],
				},
				fields=['parent'],
				limit=1,
			)

			if not duplicates:
				continue

			template = duplicates[0].parent

			template_cost_center = frappe.db.get_value(
				'Budget Template', template, 'cost_center'
			)

			if template_cost_center != self.cost_center:
				continue

			template_link = frappe.utils.get_link_to_form(
				'Budget Template', template
			)

			frappe.throw(
				_(
					'Account : <b>{0}</b> is used in the {1} Budget Template '
					'with the same Cost Center : <b>{2}</b>.'
				).format(
					row.account_head,
					template_link,
					self.cost_center,
				),
				title=_('Duplicate Account Found'),
			)

@frappe.whitelist()
def get_budget_approver_employees(doctype, txt, searchfield, start, page_len, filters):
	'''
		Fetch active employees for a given company & department
		whose user has the role `Budget Approver`.
	'''
	if not filters:
		return []

	company = filters.get('company')
	department = filters.get('department')

	if not company or not department:
		return []

	role_name = 'Budget Approver'
	query = '''
		SELECT
			emp.name,
			emp.employee_name
		FROM
			`tabEmployee` emp
			INNER JOIN `tabUser` u
				ON u.name = emp.user_id
			INNER JOIN `tabHas Role` hr
				ON hr.parent = u.name
		WHERE
			hr.role = %(role)s
			AND emp.status = 'Active'
			AND (
				emp.name LIKE %(search_txt)s
				OR emp.employee_name LIKE %(search_txt)s
			)
			AND emp.company = %(company)s
			AND emp.department = %(department)s
		LIMIT %(start)s, %(page_len)s
	'''

	# Prepare query parameters
	params = {
		'role': role_name,
		'search_txt': f'%{txt}%',
		'start': start,
		'page_len': page_len,
		'company': company,
		'department': department
	}

	# Execute query
	budget_heads = frappe.db.sql(query, params, as_list=True)
	return budget_heads
