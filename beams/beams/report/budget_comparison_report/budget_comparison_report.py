# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import datetime

import frappe
from frappe import _
from frappe.utils import flt, formatdate

from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	if filters.get("budget_against_filter"):
		dimensions = filters.get("budget_against_filter")
	else:
		dimensions = get_cost_centers(filters)

	period_month_ranges = get_period_month_ranges(filters["period"], filters["from_fiscal_year"])
	cam_map = get_dimension_account_month_map(filters)

	data = []
	for dimension in dimensions:
		dimension_items = cam_map.get(dimension)
		if dimension_items:
			data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, 0)

	chart = get_chart_data(filters, columns, data)

	return columns, data, None, chart


def get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation):
	for cost_head, monthwise_data in dimension_items.items():
		account = monthwise_data.get("account", "")
		budget_group = monthwise_data.get("budget_group", "")
		cost_category = monthwise_data.get("cost_category", "")

		row = [dimension, cost_head, account, budget_group, cost_category]
		totals = [0, 0, 0]

		for year in get_fiscal_years(filters):
			last_total = 0
			for relevant_months in period_month_ranges:
				period_data = [0, 0, 0]
				for month in relevant_months:
					if monthwise_data.get(year[0]):
						month_data = monthwise_data.get(year[0]).get(month, {})
						for i, fieldname in enumerate(["target", "actual", "variance"]):
							value = flt(month_data.get(fieldname))
							period_data[i] += value
							totals[i] += value

				period_data[0] += last_total

				if DCC_allocation:
					period_data[0] = period_data[0] * (DCC_allocation / 100)
					period_data[1] = period_data[1] * (DCC_allocation / 100)

				period_data[2] = period_data[0] - period_data[1]
				row += period_data

		totals[2] = totals[0] - totals[1]
		if filters["period"] != "Yearly":
			row += totals
		data.append(row)

	return data


def get_columns(filters):
	columns = [
		{
			"label": _(filters.get("budget_against")),
			"fieldtype": "Link",
			"fieldname": "budget_against",
			"options": filters.get("budget_against"),
			"width": 200,
		},
		{
			"label": _("Cost Head"),
			"fieldname": "cost_head",
			"fieldtype": "Link",
			"options": "Cost Head",
			"width": 200,
		},
		{
			"label": _("Account"),
			"fieldname": "Account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 220,
		},
		{
			"label": _("Budget Group"),
			"fieldname": "budget_group",
			"fieldtype": "Link",
			"options": "Budget Group",
			"width": 200,
		},
		{
			"label": _("Cost Category"),
			"fieldname": "cost_category",
			"fieldtype": "Data",
			"width": 160,
		}
	]

	group_months = False if filters["period"] == "Monthly" else True

	fiscal_year = get_fiscal_years(filters)

	for year in fiscal_year:
		for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
			if filters["period"] == "Yearly":
				labels = [
					_("Budget") + " " + str(year[0]),
					_("Actual") + " " + str(year[0]),
					_("Variance") + " " + str(year[0]),
				]
				for label in labels:
					columns.append(
						{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
					)
			else:
				for label in [
					_("Budget") + " (%s)" + " " + str(year[0]),
					_("Actual") + " (%s)" + " " + str(year[0]),
					_("Variance") + " (%s)" + " " + str(year[0]),
				]:
					if group_months:
						label = label % (
							formatdate(from_date, format_string="MMM")
							+ "-"
							+ formatdate(to_date, format_string="MMM")
						)
					else:
						label = label % formatdate(from_date, format_string="MMM")

					columns.append(
						{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
					)

	if filters["period"] != "Yearly":
		for label in [_("Total Budget"), _("Total Actual"), _("Total Variance")]:
			columns.append(
				{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
			)

		return columns
	else:
		return columns


def get_cost_centers(filters):
	order_by = ""
	if filters.get("budget_against") == "Cost Center":
		order_by = "order by lft"

	if filters.get("budget_against") in ["Cost Center", "Project"]:
		return frappe.db.sql_list(
			"""
				select
					name
				from
					`tab{tab}`
				where
					company = %s
				{order_by}
			""".format(tab=filters.get("budget_against"), order_by=order_by),
			filters.get("company"),
		)
	else:
		return frappe.db.sql_list(
			"""
				select
					name
				from
					`tab{tab}`
			""".format(tab=filters.get("budget_against"))
		)


# Get dimension & target details
def get_dimension_target_details(filters):
	budget_against = frappe.scrub(filters.get("budget_against"))
	cond = ""
	if filters.get("budget_against_filter"):
		cond += f""" and b.{budget_against} in (%s)""" % ", ".join(
			["%s"] * len(filters.get("budget_against_filter"))
		)
	if filters.get("budget_group"):
		cond += "and ba.budget_group = '{0}'".format(filters.get("budget_group"))
	if filters.get("cost_head"):
		cond += "and ba.cost_head = '{0}'".format(filters.get("cost_head"))
	if filters.get("cost_category"):
		cond += "and ba.cost_category = '{0}'".format(filters.get("cost_category"))
	if filters.get("finance_group"):
		cond += "and b.finance_group = '{0}'".format(filters.get("finance_group"))

	return frappe.db.sql(
		f"""
			select
				b.{budget_against} as budget_against,
				b.monthly_distribution,
				ba.account,
				ba.budget_amount,
				ba.budget_group,
				ba.cost_head,
				ba.cost_category,
				b.fiscal_year
			from
				`tabBudget` b,
				`tabM1 Budget Account` ba
			where
				b.name = ba.parent
				and b.fiscal_year between %s and %s
				and b.budget_against = %s
				and b.company = %s
				{cond}
			order by
				b.fiscal_year
		""",
		tuple(
			[
				filters.from_fiscal_year,
				filters.to_fiscal_year,
				filters.budget_against,
				filters.company,
			]
			+ (filters.get("budget_against_filter") or [])
		),
		as_dict=True,
	)

def get_target_distribution_details(filters):
	budget_against = frappe.scrub(filters.get("budget_against"))
	budget_against_filter = filters.get("budget_against_filter") or []
	if not budget_against_filter:
		if filters.get("budget_against") in ["Cost Center", "Project"]:
			budget_against_filter = get_cost_centers(filters)
	budget_against_data = (
		",".join(f"'{bud_ag}'" for bud_ag in budget_against_filter)
		if budget_against_filter
		else "''"
	)

	target_details = {}

	budget_query = f"""
		select
			b.name as budget_name,
			b.fiscal_year
		from
			`tabBudget` b
		where
			b.fiscal_year between %s and %s and
			b.company = %s and
			b.budget_against = %s and
			b.{budget_against} in ({budget_against_data})
	"""
	budgets = frappe.db.sql(
		budget_query,
		(filters.from_fiscal_year, filters.to_fiscal_year, filters.company, filters.budget_against),
		as_dict=True
	)

	# Loop through the Budget records to get the amounts for each month from the Budget Account child table
	for budget in budgets:
		# Get the Budget Account details for each budget
		budget_accounts = frappe.get_all(
			"M1 Budget Account",
			filters={"parent": budget.budget_name},
			fields=["cost_head", "january", "february", "march", "april", "may", "june",
					"july", "august", "september", "october", "november", "december"]
		)

		for d in budget_accounts:
			target_details.setdefault(d.cost_head, {}).setdefault(budget.fiscal_year, {})

			# Assign the actual amount for each month
			for month, amount in zip(
				["january", "february", "march", "april", "may", "june",
				 "july", "august", "september", "october", "november", "december"],
				[d.january, d.february, d.march, d.april, d.may, d.june,
				 d.july, d.august, d.september, d.october, d.november, d.december]
			):
				target_details[d.cost_head][budget.fiscal_year][month] = flt(amount)

	return target_details

def get_dimension_account_month_map(filters):
	dimension_target_details = get_dimension_target_details(filters)
	tdd = get_target_distribution_details(filters)

	cam_map = {}

	month_map = {
		"January": "january", "February": "february", "March": "march",
		"April": "april", "May": "may", "June": "june", "July": "july",
		"August": "august", "September": "september", "October": "october",
		"November": "november", "December": "december"
	}

	for ccd in dimension_target_details:
		# Ensure cost_head, budget_group, and cost_category are stored at the account level
		cam_map.setdefault(ccd.budget_against, {}).setdefault(ccd.cost_head, {
			"account": ccd.account,
			"budget_group": ccd.budget_group,
			"cost_category": ccd.cost_category
		}).setdefault(ccd.fiscal_year, {})

		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime("%B")

			cam_map[ccd.budget_against][ccd.cost_head][ccd.fiscal_year].setdefault(
				month, frappe._dict({"target": 0.0, "actual": 0.0})
			)

			tav_dict = cam_map[ccd.budget_against][ccd.cost_head][ccd.fiscal_year][month]

			tav_dict.target = tdd[ccd.cost_head][ccd.fiscal_year][month_map[month]]
			tav_dict.actual = get_actual_expenses(ccd.budget_against, ccd.cost_head, ccd.account, month, ccd.fiscal_year)
	return cam_map

# Get actual details from gl entry
def get_actual_expenses(cost_center, cost_head, account, month, fy):
	expenses = 0
	ac_details = frappe.db.sql(
		f"""
			select
				gl.account,
				gl.cost_head,
				SUM(gl.debit) as debit,
				SUM(gl.credit) as credit,
				gl.fiscal_year,
				MONTHNAME(gl.posting_date) as month_name
			from
				`tabGL Entry` gl
			where
				gl.fiscal_year = '{fy}'
				and gl.account = '{account}'
				and gl.cost_center = '{cost_center}'
				and gl.cost_head = '{cost_head}'
				and MONTHNAME(gl.posting_date) = '{month}'
			group by
				gl.cost_head
			order by
				gl.fiscal_year
		""",
		as_dict=1,
	)
	if ac_details:
		expenses = flt(ac_details[0].debit) - flt(ac_details[0].credit)
	return expenses


def get_fiscal_years(filters):
	fiscal_year = frappe.db.sql(
		"""
			select
				name
			from
				`tabFiscal Year`
			where
				name between %(from_fiscal_year)s and %(to_fiscal_year)s
		""",
		{"from_fiscal_year": filters["from_fiscal_year"], "to_fiscal_year": filters["to_fiscal_year"]},
	)

	return fiscal_year


def get_chart_data(filters, columns, data):
	if not data:
		return None

	labels = []

	fiscal_year = get_fiscal_years(filters)
	group_months = False if filters["period"] == "Monthly" else True

	for year in fiscal_year:
		for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
			if filters["period"] == "Yearly":
				labels.append(year[0])
			else:
				if group_months:
					label = (
						formatdate(from_date, format_string="MMM")
						+ "-"
						+ formatdate(to_date, format_string="MMM")
					)
					labels.append(label)
				else:
					label = formatdate(from_date, format_string="MMM")
					labels.append(label)

	no_of_columns = len(labels)

	budget_values, actual_values = [0] * no_of_columns, [0] * no_of_columns
	for d in data:
		values = d[5:]	# Start from index 5 (after cost_category)
		index = 0

		for i in range(no_of_columns):
			budget_values[i] += values[index]
			actual_values[i] += values[index + 1]
			index += 3	# Skip to the next (budget, actual, variance) set


	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Budget"), "chartType": "bar", "values": budget_values},
				{"name": _("Actual Expense"), "chartType": "bar", "values": actual_values},
			],
		},
		"type": "bar",
	}
