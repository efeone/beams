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
	for account, monthwise_data in dimension_items.items():
		cost_head = monthwise_data.get("cost_head", "")
		cost_subhead = monthwise_data.get("cost_subhead", "")
		cost_category = monthwise_data.get("cost_category", "")  # Added cost_category

		row = [dimension, account, cost_head, cost_subhead, cost_category]  # Added cost_category to row
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

				if filters.get("show_cumulative"):
					last_total = period_data[0] - period_data[1]

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
			"width": 150,
		},
		{
			"label": _("Account"),
			"fieldname": "Account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 150,
		},
		{
			"label": _("Cost Head"),
			"fieldname": "cost_head",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Cost Subhead"),
			"fieldname": "cost_subhead",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Cost Category"),
			"fieldname": "cost_category",
			"fieldtype": "Data",
			"width": 150,
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
		)  # nosec


# Get dimension & target details
def get_dimension_target_details(filters):
	budget_against = frappe.scrub(filters.get("budget_against"))
	cond = ""
	if filters.get("budget_against_filter"):
		cond += f""" and b.{budget_against} in (%s)""" % ", ".join(
			["%s"] * len(filters.get("budget_against_filter"))
		)
	if filters.get("cost_head"):
		cond += "and ba.cost_head = '{0}'".format(filters.get("cost_head"))
	if filters.get("cost_subhead"):
		cond += "and ba.cost_subhead = '{0}'".format(filters.get("cost_subhead"))
	if filters.get("cost_category"):
		cond += "and ba.cost_category = '{0}'".format(filters.get("cost_category"))

	return frappe.db.sql(
		f"""
			select
				b.{budget_against} as budget_against,
				b.monthly_distribution,
				ba.account,
				ba.budget_amount,
				ba.cost_head,
				ba.cost_subhead,
				ba.cost_category,  -- Added cost_category field
				b.fiscal_year
			from
				`tabBudget` b,
				`tabBudget Account` ba
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
	target_details = {}

	# Loop through the Budget records to get the amounts for each month from the Budget Account child table
	for budget in frappe.db.sql(
		"""
			select
				b.name as budget_name,
				b.fiscal_year
			from
				`tabBudget` b
			where
				b.fiscal_year between %s and %s
		""",
		(filters.from_fiscal_year, filters.to_fiscal_year),
		as_dict=True,
	):
		# Get the Budget Account details for each budget
		budget_accounts = frappe.get_all(
			"Budget Account",
			filters={"parent": budget.budget_name},
			fields=["account", "january", "february", "march", "april", "may", "june",
					"july", "august", "september", "october", "november", "december"]
		)

		for d in budget_accounts:
			target_details.setdefault(d.account, {}).setdefault(budget.fiscal_year, {})

			# Assign the actual amount for each month
			for month, amount in zip(
				["january", "february", "march", "april", "may", "june",
				 "july", "august", "september", "october", "november", "december"],
				[d.january, d.february, d.march, d.april, d.may, d.june,
				 d.july, d.august, d.september, d.october, d.november, d.december]
			):
				target_details[d.account][budget.fiscal_year][month] = flt(amount)


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
		actual_details = get_actual_details(ccd.budget_against, filters)

		# Ensure cost_head, cost_subhead, and cost_category are stored at the account level
		cam_map.setdefault(ccd.budget_against, {}).setdefault(ccd.account, {
			"cost_head": ccd.cost_head,
			"cost_subhead": ccd.cost_subhead,
			"cost_category": ccd.cost_category  # Added cost_category
		}).setdefault(ccd.fiscal_year, {})

		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime("%B")

			cam_map[ccd.budget_against][ccd.account][ccd.fiscal_year].setdefault(
				month, frappe._dict({"target": 0.0, "actual": 0.0})
			)

			tav_dict = cam_map[ccd.budget_against][ccd.account][ccd.fiscal_year][month]

			month_percentage = (
				tdd.get(ccd.monthly_distribution, {}).get(month, 0)
				if ccd.monthly_distribution
				else 100.0 / 12
			)

			tav_dict.target = tdd[ccd.account][ccd.fiscal_year][month_map[month]]

			for ad in actual_details.get(ccd.account, []):
				if ad.month_name == month and ad.fiscal_year == ccd.fiscal_year:
					tav_dict.actual += flt(ad.debit) - flt(ad.credit)

	return cam_map

# Get actual details from gl entry
def get_actual_details(name, filters):
	budget_against = frappe.scrub(filters.get("budget_against"))
	cond = ""

	if filters.get("budget_against") == "Cost Center":
		cc_lft, cc_rgt = frappe.db.get_value("Cost Center", name, ["lft", "rgt"])
		cond = f"""
				and lft >= "{cc_lft}"
				and rgt <= "{cc_rgt}"
			"""

	ac_details = frappe.db.sql(
		f"""
			select
				gl.account,
				gl.debit,
				gl.credit,
				gl.fiscal_year,
				MONTHNAME(gl.posting_date) as month_name,
				b.{budget_against} as budget_against
			from
				`tabGL Entry` gl,
				`tabBudget Account` ba,
				`tabBudget` b
			where
				b.name = ba.parent
				and ba.account=gl.account
				and b.{budget_against} = gl.{budget_against}
				and gl.fiscal_year between %s and %s
				and b.{budget_against} = %s
				and exists(
					select
						name
					from
						`tab{filters.budget_against}`
					where
						name = gl.{budget_against}
						{cond}
				)
				group by
					gl.name
				order by gl.fiscal_year
		""",
		(filters.from_fiscal_year, filters.to_fiscal_year, name),
		as_dict=1,
	)

	cc_actual_details = {}
	for d in ac_details:
		cc_actual_details.setdefault(d.account, []).append(d)

	return cc_actual_details


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
		values = d[5:]  # Start from index 5 (after cost_category)
		index = 0

		for i in range(no_of_columns):
			budget_values[i] += values[index]
			actual_values[i] += values[index + 1]
			index += 3  # Skip to the next (budget, actual, variance) set


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
