# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import get_absolute_url

month_fields = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

class BudgetTool(Document):
	def validate(self):
		frappe.throw('You were not able to do this action. Please try again.')

@frappe.whitelist()
def get_budget_html(budget):
	'''
		Method to create Budget if it is not created
	'''
	html_data = '<p>No Budget forund with Budget ID : <b>{0}</b> </p>'.format(budget)
	is_editable = 0
	if frappe.db.exists('Budget', budget):
		# Defining Columns
		columns = ['Cost Head', 'Budget Group', 'Account Head', 'Cost Category', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total Budget']

		# Building Data
		data = []
		budget_doc = frappe.get_doc('Budget', budget)
		is_editable = 1
		values_read_only = 0
		if budget_doc.docstatus:
			is_editable = 0
			values_read_only = 1
		for row in budget_doc.budget_accounts:
			budget_row = get_budget_item_details(row.name, values_read_only)
			data.append(budget_row)
		total_row = ''
		html_data = frappe.render_template('beams/doctype/budget_tool/budget_tool.html', {
			'columns': columns,
			'data': data,
			'total_row': total_row
		})
	return {
		'html':html_data,
		'is_editable': is_editable
	}

def get_budget_item_details(row_id, read_only=0):
	'''
		Method to get Budget Account Row Details
	'''
	data = []
	if frappe.db.exists('M1 Budget Account', row_id):
		row_detail = frappe.get_doc('M1 Budget Account', row_id)
		# Set Master Links
		data.append({ 'type':'text', 'value': row_detail.cost_head, 'read_only':1, 'primary': 1, 'ref_link': get_absolute_url('Cost Head', row_detail.cost_head) })
		data.append({ 'type':'text', 'value': row_detail.budget_group, 'read_only':1, 'primary': 1, 'ref_link': get_absolute_url('Budget Group', row_detail.budget_group) })
		data.append({ 'type':'text', 'value': row_detail.account, 'read_only':1, 'primary': 1, 'ref_link': get_absolute_url('Account', row_detail.account) })
		data.append({ 'type':'text', 'value': row_detail.cost_category, 'read_only':1, 'primary': 1, 'ref_link': get_absolute_url('Cost Category', row_detail.cost_category) })
		# Monthly Distribution
		for field_name in month_fields:
			data.append({ 'type':'number', 'value': int(row_detail.get(field_name)), 'read_only':read_only, 'class_name':'text-right month_input'})
		data.append({ 'type':'number', 'value': int(row_detail.budget_amount), 'read_only':1, 'class_name':'text-right total_budget' })
	return data

@frappe.whitelist()
def save_budget_data(budget, data):
	if frappe.db.exists('Budget', budget):
		budget_doc = frappe.get_doc('Budget', budget)
		data = json.loads(data)
		row_idx = 0
		# Update Budget Rows
		for budget_row in budget_doc.budget_accounts:
			month_idx = 5
			budget_total = 0
			for month in month_fields:
				value = 0
				try:
					value = int(data[row_idx][month_idx]) or 0
				except:
					pass
				budget_total += value
				budget_row.set(month, value)
				month_idx += 1
			budget_row.budget_amount = budget_total
			row_idx += 1
		budget_doc.flags.ignore_mandatory = 1
		budget_doc.save(ignore_permissions=True)
	return 1

@frappe.whitelist()
def add_budget_row(budget, cost_head):
	'''
		Method to add a row in Budget
	'''
	if frappe.db.exists('Budget', budget):
		budget_doc = frappe.get_doc('Budget', budget)
		budget_row = budget_doc.append('budget_accounts')
		if frappe.db.exists('Cost Head', cost_head):
			cost_head_doc = frappe.get_doc('Cost Head', cost_head)
			budget_row.cost_head = cost_head_doc.name
			budget_row.budget_group = cost_head_doc.budget_group
			budget_row.cost_category = cost_head_doc.cost_category
			for account in cost_head_doc.accounts:
				if account.company == budget_doc.company:
					budget_row.account = account.default_account
					break
		budget_doc.flags.ignore_mandatory = 1
		budget_doc.save(ignore_permissions=True)
	return 1

@frappe.whitelist()
def get_cost_head_details(cost_head):
	'''
		Method to get Cost Head Details
	'''
	if frappe.db.exists('Cost Head', cost_head):
		cost_head_doc = frappe.get_doc('Cost Head', cost_head)
		return {
			'cost_head': cost_head_doc.name,
			'budget_group': cost_head_doc.budget_group,
			'cost_category': cost_head_doc.cost_category
		}
	return {}