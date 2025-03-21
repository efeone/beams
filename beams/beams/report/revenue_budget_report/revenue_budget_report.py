# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, formatdate
from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    if not data:
        return columns, []

    return columns, data

def get_columns(filters):
    columns = [
        {
            'fieldname': 'name',
            'label': 'Name',
            'fieldtype': 'Data',
            'width': 500
        }
    ]
    fiscal_year = filters.get('fiscal_year')
    period = filters.get('period')
    month_name = filters.get('month')
    group_months = False if period == 'Monthly' else True
    currency_fields = []
    if month_name:
        label = 'Revenue ({0})'.format(month_name)
        currency_fields.append(frappe.scrub(label))
        columns.append(
            {'label': label, 'fieldtype': 'Currency', 'fieldname': frappe.scrub(label), 'width': 200}
        )
        filters["currency_fields"] = currency_fields
        return columns
    for from_date, to_date in get_period_date_ranges(period, fiscal_year):
        if period == 'Yearly':
            label = _('Revenue')
            columns.append(
                {'label': label, 'fieldtype': 'Currency', 'fieldname': 'total_revenue', 'width': 200}
            )
            currency_fields.append('total_revenue')
        else:
            for label in [
                _('Revenue') + ' (%s)',
            ]:
                if group_months:
                    label = label % (
                        formatdate(from_date, format_string='MMM')
                        + '-'
                        + formatdate(to_date, format_string='MMM')
                    )
                else:
                    label = label % formatdate(from_date, format_string='MMM')

                currency_fields.append(frappe.scrub(label))
                columns.append(
                    {'label': label, 'fieldtype': 'Currency', 'fieldname': frappe.scrub(label), 'width': 200}
                )
    if period != 'Yearly' and (period =='Monthly' or not month_name):
        currency_fields.append('total_revenue')
        columns.append(
            {'label': _('Total Revenue'), 'fieldtype': 'Currency', 'fieldname': 'total_revenue', 'width': 200}
        )
    filters["currency_fields"] = currency_fields
    return columns

def get_data(filters=None):
    data = []
    period = filters.get('period', 'Yearly')
    fiscal_year = filters.get('fiscal_year')

    #Get Months list as per fiscal year
    period_month_ranges = get_period_month_ranges('Monthly', fiscal_year)
    months_order = [f"{month[0].lower()}" for month in period_month_ranges]

    # Dictionary to store budget amounts for each parent
    currency_fields = filters.get("currency_fields", ["total_revenue"])
    revenue_map = {}

    if filters.get('company'):
        companies = [filters.get('company')]
    else:
        companies = frappe.get_all('Company', pluck='name')

    for company in companies:
        abbr = frappe.db.get_value('Company', company, 'abbr')
        data.append({'id': abbr, 'parent': '', 'indent': 0, 'name': company, 'total_revenue': 0})
        revenue_map[abbr] = {field: 0 for field in currency_fields}# Initialize parent total

        categories = get_categories(company, fiscal_year)
        for cat in categories:
            data.append({'id': cat, 'parent': abbr, 'indent': 1, 'name': cat, 'total_revenue': 0})
            revenue_map[cat] = {field: 0 for field in currency_fields}

            revenue_groups = get_revenue_groups(company, fiscal_year, cat)
            for group in revenue_groups:
                data.append({'id': group, 'parent': cat, 'indent': 2, 'name': group, 'total_revenue': 0})
                revenue_map[group] = {field: 0 for field in currency_fields}

                centres = get_centers(company, fiscal_year, group)
                for centre in centres:
                    centre_name = centre.get('revenue_centre', '')
                    row_id = centre.get('name', '')
                    total_revenue = centre.get('total_revenue', 0)
                    rc_row = {
                        'id': centre_name,
                        'parent': group,
                        'indent': 3,
                        'name': centre_name,
                        'total_revenue': total_revenue
                    }
                    if period != 'Yearly':
                        revenue_column_data = get_revenue_column_data(period, months_order, row_id)
                        rc_row.update(revenue_column_data)
                    data.append(rc_row)

                    for field in currency_fields:
                        revenue_map[group][field] += rc_row.get(field, 0)

                for field in currency_fields:
                    revenue_map[cat][field] += revenue_map[group][field]

            for field in currency_fields:
                revenue_map[abbr][field] += revenue_map[cat][field]

     # Update budget amounts in the data list
    for row in data:
        row.update(revenue_map.get(row['id'], {}))
    return data

def get_categories(company, fiscal_year):
    '''
        Method to get Revenue Categories
    '''
    query = '''
        SELECT
            DISTINCT br.revenue_category
        FROM
            `tabRevenue Budget` br
        WHERE
            br.fiscal_year = %(fiscal_year)s AND
            br.company = %(company)s
    '''
    query_filters = {
        'company':company,
        'fiscal_year':fiscal_year
    }
    cost_categories = frappe.db.sql(query, query_filters, as_dict=True)
    return [row.revenue_category for row in cost_categories]

def get_revenue_groups(company, fiscal_year, revenue_category):
    '''
        Method to get Revenue Categories
    '''
    query = '''
        SELECT
            DISTINCT br.revenue_group
        FROM
            `tabRevenue Budget` br
        WHERE
            br.fiscal_year = %(fiscal_year)s AND
            br.revenue_category = %(revenue_category)s AND
            br.company = %(company)s
    '''
    query_filters = {
        'company':company,
        'fiscal_year':fiscal_year,
        'revenue_category':revenue_category
    }
    revenue_groups = frappe.db.sql(query, query_filters, as_dict=True)
    return [row.revenue_group for row in revenue_groups]

def get_centers(company, fiscal_year, revenue_group):
    '''
        Method to get Revenue Centres
    '''
    query = '''
        SELECT
            ra.revenue_centre,
            ra.name,
            ra.revenue_amount as total_revenue
        FROM
            `tabRevenue Account` ra
        JOIN
            `tabRevenue Budget` br ON ra.parent = br.name
        WHERE
            br.fiscal_year = %(fiscal_year)s AND
            br.company = %(company)s AND
            br.revenue_group = %(revenue_group)s
    '''
    query_filters = {
        'company': company,
        'fiscal_year': fiscal_year,
        'revenue_group': revenue_group
    }
    revenue_centres = frappe.db.sql(query, query_filters, as_dict=True)
    return revenue_centres

def get_revenue_column_data(period, months_order, row_id):
    '''
        Get Columnar data specif to period
    '''
    revenue_column_data = {}
    if frappe.db.exists('Revenue Account', row_id):
        data = frappe.db.get_value('Revenue Account', row_id, fieldname=months_order, as_dict=True)
        if period == 'Monthly':
            for month in months_order:
                label = 'revenue_({0})'.format(month[0:3])
                revenue_column_data[label] = data.get(month)
        if period == 'Quarterly':
            total = 0
            for i, month in enumerate(months_order):
                total += data.get(month)
                if i in [2, 5, 8, 11]:
                    label = 'revenue_({0}_{1})'.format(months_order[i-2][0:3], month[0:3])
                    revenue_column_data[label] = total
                    total = 0
        if period == 'Half-Yearly':
            total = 0
            for i, month in enumerate(months_order):
                total += data.get(month)
                if i in [5, 11]:
                    label = 'revenue_({0}_{1})'.format(months_order[i-5][0:3], month[0:3])
                    revenue_column_data[label] = total
                    total = 0
    return revenue_column_data