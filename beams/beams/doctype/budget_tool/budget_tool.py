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
		columns = ['Cost Head', 'Cost Sub Head', 'Cost Category', 'Cost Description', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total Budget']

        # Building Data
		data = []
		budget_doc = frappe.get_doc('Budget', budget)
		is_editable = 1
		values_read_only = 0
		if budget_doc.docstatus:
			is_editable = 0
			values_read_only = 1
		for row in budget_doc.accounts:
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
	if frappe.db.exists('Budget Account', row_id):
		row_detail = frappe.get_doc('Budget Account', row_id)
		# Set Master Links
		data.append({ 'type':'text', 'value': row_detail.cost_head, 'read_only':1, 'primary': 1, 'ref_link': get_absolute_url('Cost Head', row_detail.cost_head) })
		data.append({ 'type':'text', 'value': row_detail.cost_subhead, 'read_only':1, 'primary': 1, 'ref_link': get_absolute_url('Cost Subhead', row_detail.cost_subhead) })
		data.append({ 'type':'text', 'value': row_detail.cost_category, 'read_only':1, 'primary': 1, 'ref_link': get_absolute_url('Cost Category', row_detail.cost_category) })
		data.append({ 'type':'text', 'value': row_detail.cost_description or '', 'read_only':read_only, 'class_name':'budget_notes' })
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
		for budget_row in budget_doc.accounts:
			month_idx = 5
			budget_total = 0
			cost_description = data[row_idx][4] or ''
			budget_row.cost_description = cost_description
			for month in month_fields:
				value = int(data[row_idx][month_idx]) or 0
				budget_total += value
				budget_row.set(month, value)
				month_idx += 1
			budget_row.budget_amount = budget_total
			row_idx += 1
		budget_doc.flags.ignore_mandatory = 1
		budget_doc.save(ignore_permissions=True)
	return 1

@frappe.whitelist()
def add_budget_row(budget, cost_head, cost_subhead, cost_category):
	'''
        Method to add a row in Budget
	'''
	if frappe.db.exists('Budget', budget):
		budget_doc = frappe.get_doc('Budget', budget)
		budget_row = budget_doc.append('accounts')
		if frappe.db.exists('Cost Head', cost_head):
			budget_row.cost_head = cost_head
		if frappe.db.exists('Cost Subhead', cost_subhead):
			budget_row.cost_subhead = cost_subhead
			budget_row.account = frappe.get_value('Cost Subhead', cost_subhead, 'account')
		if frappe.db.exists('Cost Category', cost_category):
			budget_row.cost_category = cost_category
		budget_doc.flags.ignore_mandatory = 1
		budget_doc.save(ignore_permissions=True)
	return 1