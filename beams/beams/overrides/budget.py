# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import add_months, flt, fmt_money, get_last_day, getdate

#for_check_only is used for early budget check on draft for PO and MR
def validate_expense_against_budget(args, expense_amount=0, for_check_only=0):
	args = frappe._dict(args)
	if not frappe.get_all('Budget', limit=1):
		return

	if args.get('company') and not args.fiscal_year:
		args.fiscal_year = get_fiscal_year(args.get('posting_date'), company=args.get('company'))[0]
		frappe.flags.exception_approver_role = frappe.get_cached_value(
			'Company', args.get('company'), 'exception_budget_approver_role'
		)

	if not frappe.get_cached_value('Budget', {'fiscal_year': args.fiscal_year, 'company': args.company}):  # nosec
		return

	if not args.account:
		args.account = args.get('expense_account')

	if not (args.get('account') and args.get('cost_center')) and args.item_code:
		args.cost_center, args.account = get_item_details(args)

	if not args.account:
		return

	default_dimensions = [
		{
			'fieldname': 'project',
			'document_type': 'Project',
		},
		{
			'fieldname': 'cost_center',
			'document_type': 'Cost Center',
		}
	]

	for dimension in default_dimensions:
		budget_against = dimension.get('fieldname')

		if (
			args.get(budget_against)
			and args.account
			and (frappe.get_cached_value('Account', args.account, 'root_type') == 'Expense')
		):
			doctype = dimension.get('document_type')

			if frappe.get_cached_value('DocType', doctype, 'is_tree'):
				lft, rgt = frappe.get_cached_value(doctype, args.get(budget_against), ['lft', 'rgt'])
				condition = f'''and exists(select name from `tab{doctype}`
					where lft<={lft} and rgt>={rgt} and name=b.{budget_against})'''  # nosec
				args.is_tree = True
			else:
				condition = f'and b.{budget_against}={frappe.db.escape(args.get(budget_against))}'
				args.is_tree = False

			args.budget_against_field = budget_against
			args.budget_against_doctype = doctype

			budget_records = frappe.db.sql(
				f'''
				select
					b.name, b.{budget_against} as budget_against, ba.budget_amount, b.monthly_distribution,
					ifnull(b.applicable_on_material_request, 0) as for_material_request,
					ifnull(applicable_on_purchase_order, 0) as for_purchase_order,
					ifnull(applicable_on_booking_actual_expenses,0) as for_actual_expenses,
					b.action_if_annual_budget_exceeded, b.action_if_accumulated_monthly_budget_exceeded,
					b.action_if_annual_budget_exceeded_on_mr, b.action_if_accumulated_monthly_budget_exceeded_on_mr,
					b.action_if_annual_budget_exceeded_on_po, b.action_if_accumulated_monthly_budget_exceeded_on_po
				from
					`tabBudget` b, `tabBudget Account` ba
				where
					b.name=ba.parent and b.fiscal_year=%s
					and ba.account=%s and b.docstatus=1
					{condition}
			''',
				(args.fiscal_year, args.account),
				as_dict=True,
			)  # nosec

			if budget_records:
				validate_budget_records(args, budget_records, expense_amount, for_check_only)


def validate_budget_records(args, budget_records, expense_amount, for_check_only):
	for budget in budget_records:
		if flt(budget.budget_amount):
			yearly_action, monthly_action = get_actions(args, budget)
			args['for_material_request'] = budget.for_material_request
			args['for_purchase_order'] = budget.for_purchase_order

			if yearly_action in ('Stop', 'Warn'):
				budget_amount = get_yearly_budget_amount(budget.name, cost_head=args.get('cost_head'))
				compare_expense_with_budget(
					args,
					budget_amount,
					_('Annual'),
					yearly_action,
					budget.budget_against,
					expense_amount,
					for_check_only
				)

			if monthly_action in ['Stop', 'Warn']:
				budget_amount = get_accumulated_monthly_budget(
					budget.name, args.posting_date, args.fiscal_year, budget.budget_amount, args.cost_head
				)

				args['month_end_date'] = get_last_day(args.posting_date)

				compare_expense_with_budget(
					args,
					budget_amount,
					_('Accumulated Monthly'),
					monthly_action,
					budget.budget_against,
					expense_amount,
					for_check_only
				)

def compare_expense_with_budget(args, budget_amount, action_for, action, budget_against, amount=0, for_check_only=0):
	#Setting doctype and docname for setting is_budget_exceeded field
	doctype, docname = None, None
	if args.get('doctype') and args.get('parent'):
		doctype = args.get('doctype')
		docname = args.get('parent')
	elif args.get('voucher_type') and args.get('voucher_no'):
		doctype = args.get('voucher_type')
		docname = args.get('voucher_no')

	args.actual_expense, args.requested_amount, args.ordered_amount = get_actual_expense(args), 0, 0
	if not amount:
		args.requested_amount, args.ordered_amount = get_requested_amount(args), get_ordered_amount(args)

		if args.get('doctype') == 'Material Request' and args.for_material_request:
			amount = args.requested_amount + args.ordered_amount

		elif args.get('doctype') == 'Purchase Order' and args.for_purchase_order:
			amount = args.ordered_amount

	total_expense = args.actual_expense + amount

	if total_expense > budget_amount:
		if args.actual_expense > budget_amount:
			error_tense = _('is already')
			diff = args.actual_expense - budget_amount
		else:
			error_tense = _('will be')
			diff = total_expense - budget_amount

		currency = frappe.get_cached_value('Company', args.company, 'default_currency')

		msg = _('{0} Budget for Account {1} with Cost Head {2} against {3} {4} is {5}. It {6} exceed by {7}').format(
			_(action_for),
			frappe.bold(args.account),
			frappe.bold(args.get('cost_head', 'N/A')),
			frappe.unscrub(args.budget_against_field),
			frappe.bold(budget_against),
			frappe.bold(fmt_money(budget_amount, currency=currency)),
			error_tense,
			frappe.bold(fmt_money(diff, currency=currency)),
		)

		msg += get_expense_breakup(args, currency, budget_against)

		if frappe.flags.exception_approver_role and frappe.flags.exception_approver_role in frappe.get_roles(
			frappe.session.user
		):
			action = 'Warn'

		#Setting Checkboxes for Budget Exceeded in the respective Doctypes
		if doctype and docname:
			if field_exists(doctype, 'is_budget_exceededed') and frappe.db.exists(doctype, docname):
				frappe.db.set_value(doctype, docname, 'is_budget_exceeded', 1, update_modified=False)
		
		if for_check_only:
			#For custom check on validate
			frappe.msgprint(msg, indicator='orange', title=_('Budget Exceeded'))
		else:
			if action == 'Stop':
				frappe.throw(msg, title=_('Budget Exceeded'))
			else:
				frappe.msgprint(msg, indicator='orange', title=_('Budget Exceeded'))
	else:
		if doctype and docname:
			if field_exists(doctype, 'is_budget_exceeded') and frappe.db.exists(doctype, docname):
				frappe.db.set_value(doctype, docname, 'is_budget_exceeded', 0, update_modified=False)

def get_expense_breakup(args, currency, budget_against):
	msg = '<hr>Total Expenses booked through - <ul>'

	common_filters = frappe._dict(
		{
			args.budget_against_field: budget_against,
			'account': args.account,
			'company': args.company,
			'cost_head': args.get('cost_head'),
		}
	)

	msg += (
		'<li>'
		+ frappe.utils.get_link_to_report(
			'General Ledger',
			label='Actual Expenses',
			filters=common_filters.copy().update(
				{
					'from_date': frappe.get_cached_value('Fiscal Year', args.fiscal_year, 'year_start_date'),
					'to_date': frappe.get_cached_value('Fiscal Year', args.fiscal_year, 'year_end_date'),
					'is_cancelled': 0,
				}
			),
		)
		+ ' - '
		+ frappe.bold(fmt_money(args.actual_expense, currency=currency))
		+ '</li>'
	)

	msg += (
		'<li>'
		+ frappe.utils.get_link_to_report(
			'Material Request',
			label='Material Requests',
			report_type='Report Builder',
			doctype='Material Request',
			filters=common_filters.copy().update(
				{
					'status': [['!=', 'Stopped']],
					'docstatus': 1,
					'material_request_type': 'Purchase',
					'item_code': args.item_code,
					'per_ordered': [['<', 100]],
				}
			),
		)
		+ ' - '
		+ frappe.bold(fmt_money(args.requested_amount, currency=currency))
		+ '</li>'
	)

	msg += (
		'<li>'
		+ frappe.utils.get_link_to_report(
			'Purchase Order',
			label='Unbilled Orders',
			report_type='Report Builder',
			doctype='Purchase Order',
			filters=common_filters.copy().update(
				{
					'status': [['!=', 'Closed']],
					'docstatus': 1,
					'item_code': args.item_code,
					'per_billed': [['<', 100]],
				}
			),
		)
		+ ' - '
		+ frappe.bold(fmt_money(args.ordered_amount, currency=currency))
		+ '</li></ul>'
	)

	return msg


def get_actions(args, budget):
	yearly_action = budget.action_if_annual_budget_exceeded
	monthly_action = budget.action_if_accumulated_monthly_budget_exceeded

	if args.get('doctype') == 'Material Request' and budget.for_material_request:
		yearly_action = budget.action_if_annual_budget_exceeded_on_mr
		monthly_action = budget.action_if_accumulated_monthly_budget_exceeded_on_mr

	elif args.get('doctype') == 'Purchase Order' and budget.for_purchase_order:
		yearly_action = budget.action_if_annual_budget_exceeded_on_po
		monthly_action = budget.action_if_accumulated_monthly_budget_exceeded_on_po

	return yearly_action, monthly_action

def get_requested_amount(args):
	item_code = args.get('item_code')
	cost_head = args.get('cost_head', '')
	condition = get_other_condition(args, 'Material Request')

	request_query = f'''
		select
			ifnull((sum(child.stock_qty - child.ordered_qty) * rate), 0) as amount
		from
			`tabMaterial Request Item` child,
			`tabMaterial Request` parent
		where
			parent.name = child.parent and
			child.item_code = '{item_code}' and
			child.cost_head = '{cost_head}' and
			parent.docstatus = 1 and
			child.stock_qty > child.ordered_qty and 
			{condition} and
			parent.material_request_type = 'Purchase' and
			parent.status != 'Stopped'
	'''
	data = frappe.db.sql(request_query, as_list=1)

	if args.get('doctype') == 'Material Request' and args.get('object'):
		unsubmitted_requested_amount = 0
		for item in args.get('object').items:
			if item.get('cost_head', '') == cost_head:
				unsubmitted_requested_amount += (item.stock_qty - item.ordered_qty) * item.rate

		data[0][0] += unsubmitted_requested_amount
		return data[0][0] if data else 0


def get_ordered_amount(args):
	item_code = args.get('item_code')
	cost_head = args.get('cost_head', '')
	condition = get_other_condition(args, 'Purchase Order')

	order_query = f'''
		select
			ifnull(sum(child.amount - child.billed_amt), 0) as amount
		from
			`tabPurchase Order Item` child,
			`tabPurchase Order` parent
		where
			parent.name = child.parent and
			child.item_code = '{item_code}' and
			child.cost_head = '{cost_head}' and
			parent.docstatus = 1 and
			child.amount > child.billed_amt and 
			parent.status != 'Closed' and
			{condition}
	'''
	data = frappe.db.sql(order_query, as_list=1)

	if args.get('doctype') == 'Purchase Order' and args.get('object'):
		unsubmitted_ordered_amount = 0
		for item in args.get('object').items:
			if item.get('cost_head', '') == cost_head:
				unsubmitted_ordered_amount += item.amount - item.billed_amt

		data[0][0] += unsubmitted_ordered_amount
	return data[0][0] if data else 0

def get_other_condition(args, for_doc):
	condition = 'expense_account = "%s"' % (args.expense_account)
	budget_against_field = args.get('budget_against_field')

	if budget_against_field and args.get(budget_against_field):
		condition += f' and child.{budget_against_field} = "{args.get(budget_against_field)}"'

	if args.get('fiscal_year'):
		date_field = 'schedule_date' if for_doc == 'Material Request' else 'transaction_date'
		start_date, end_date = frappe.get_cached_value(
			'Fiscal Year', args.get('fiscal_year'), ['year_start_date', 'year_end_date']
		)

		condition += f''' and parent.{date_field}
			between '{start_date}' and '{end_date}' '''

	return condition


def get_actual_expense(args):
	'''
		Method to get Actual Expense from GL Entry
	'''

	#Checking Cost Head based expenses
	condition3 = ''
	if field_exists('GL Entry', 'cost_head'):
		condition3 = 'and gle.cost_head = %(cost_head)s'

	if not args.budget_against_doctype:
		args.budget_against_doctype = frappe.unscrub(args.budget_against_field)

	budget_against_field = args.get('budget_against_field')
	condition1 = ' and gle.posting_date <= %(month_end_date)s' if args.get('month_end_date') else ''

	if args.is_tree:
		lft_rgt = frappe.db.get_value(
			args.budget_against_doctype, args.get(budget_against_field), ['lft', 'rgt'], as_dict=1
		)

		args.update(lft_rgt)

		condition2 = f'''and exists(select name from `tab{args.budget_against_doctype}`
			where lft>=%(lft)s and rgt<=%(rgt)s
			and name=gle.{budget_against_field})'''
	else:
		condition2 = f'''and exists(select name from `tab{args.budget_against_doctype}`
		where name=gle.{budget_against_field} and
		gle.{budget_against_field} = %({budget_against_field})s)'''

	amount = flt(
		frappe.db.sql(
			f'''
		select sum(gle.debit) - sum(gle.credit)
		from `tabGL Entry` gle
		where
			is_cancelled = 0
			and gle.account=%(account)s
			{condition1}
			and gle.fiscal_year=%(fiscal_year)s
			and gle.company=%(company)s
			and gle.docstatus=1
			{condition2}
			{condition3}
	''',
			(args),
		)[0][0]
	)# nosec

	return amount


def get_accumulated_monthly_budget(monthly_distribution, posting_date, fiscal_year, annual_budget, cost_head):
	'''
		Method to get Accumulated Monthly Budget for the selected Cost Head
	'''
	# List of months explicitly defined
	months = [
		'january', 'february', 'march', 'april', 'may', 'june',
		'july', 'august', 'september', 'october', 'november', 'december'
	]

	dt = frappe.get_cached_value('Fiscal Year', fiscal_year, 'year_start_date')

	accummulated_budget = 0

	while dt <= getdate(posting_date):
		accummulated_budget += frappe.db.get_value('M1 Budget Account', {'parent':monthly_distribution, 'cost_head':cost_head}, months[dt.month - 1]) or 0
		dt = add_months(dt, 1)

	return accummulated_budget

def get_item_details(args):
	cost_center, expense_account = None, None

	if not args.get('company'):
		return cost_center, expense_account

	if args.item_code:
		item_defaults = frappe.db.get_value('Item Default',{
				'parent': args.item_code,
				'company': args.get('company')
			},
			['buying_cost_center', 'expense_account'],
		)
		if item_defaults:
			cost_center, expense_account = item_defaults

	if not (cost_center and expense_account):
		for doctype in ['Item Group', 'Company']:
			data = get_expense_cost_center(doctype, args)

			if not cost_center and data:
				cost_center = data[0]

			if not expense_account and data:
				expense_account = data[1]

			if cost_center and expense_account:
				return cost_center, expense_account

	return cost_center, expense_account

def get_expense_cost_center(doctype, args):
	'''
		Method to get Expense Account and Cost Center from Item Group and Company
	'''
	if doctype == 'Item Group':
		return frappe.db.get_value('Item Default',{
				'parent': args.get(frappe.scrub(doctype)), 
				'company': args.get('company')
			},
			['buying_cost_center', 'expense_account'],
		)
	else:
		return frappe.db.get_value(
			doctype, args.get(frappe.scrub(doctype)), ['cost_center', 'default_expense_account']
		)

def field_exists(doctype, fieldname):
	'''
		Method to check wether field exists or not in a doctype
	'''
	meta = frappe.get_meta(doctype)
	return meta.has_field(fieldname)

def get_yearly_budget_amount(budget_id, cost_head=None):
	'''
		Method to get Budget Amount for the selected Cost Head in the annual budget
	'''
	budget_amount = frappe.db.get_value('M1 Budget Account', {'parent': budget_id, 'cost_head': cost_head}, 'budget_amount') or 0
	return budget_amount
