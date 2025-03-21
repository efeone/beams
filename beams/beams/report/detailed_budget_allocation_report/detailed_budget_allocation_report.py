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
        label = 'Budget ({0})'.format(month_name)
        currency_fields.append(frappe.scrub(label))
        columns.append(
            {'label': label, 'fieldtype': 'Currency', 'fieldname': frappe.scrub(label), 'width': 200}
        )
        filters["currency_fields"] = currency_fields
        return columns
    for from_date, to_date in get_period_date_ranges(period, fiscal_year):
        if period == 'Yearly':
            label = _('Budget')
            columns.append(
                {'label': label, 'fieldtype': 'Currency', 'fieldname': 'total_budget', 'width': 200}
            )
            currency_fields.append('total_budget')
        else:
            for label in [
                _('Budget') + ' (%s)',
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
        currency_fields.append('total_budget')
        columns.append(
            {'label': _('Total Budget'), 'fieldtype': 'Currency', 'fieldname': 'total_budget', 'width': 200}
        )
    filters["currency_fields"] = currency_fields
    return columns

def get_data(filters):
    data = []
    period = filters.get('period', 'Yearly')
    fiscal_year = filters.get('fiscal_year')
    cost_category = filters.get('cost_category', '')
    division = filters.get('division', '')
    sort_by_filter = filters.get('sort_by', 'DESC')

    #Get Months list as per fiscal year
    period_month_ranges = get_period_month_ranges('Monthly', fiscal_year)
    months_order = [f"{month[0].lower()}_inr" for month in period_month_ranges]

    # Dictionary to store budget amounts for each parent
    currency_fields = filters.get("currency_fields", ["total_budget"])
    budget_map = {}

    if filters.get('company'):
        companies = [filters.get('company')]
    else:
        companies = frappe.get_all('Company', pluck='name')

    for company in companies:
        abbr = frappe.db.get_value('Company', company, 'abbr')
        data.append({'id': abbr, 'parent': '', 'indent': 0, 'name': company, 'total_budget': 0})
        budget_map[abbr] = {field: 0 for field in currency_fields}# Initialize parent total

        if filters.get('region'):
            if filters.get('region') == 'GCC':
                finance_groups = ['GCC']
            else:
                finance_groups = frappe.get_all('Finance Group', { 'name': ['!=', 'GCC'] }, pluck='name')
        else:
            finance_groups = frappe.get_all('Finance Group', pluck='name')

        for fg in finance_groups:
            fg_id = f'{fg}-{abbr}'
            data.append({'id': fg_id, 'parent': abbr, 'indent': 1, 'name': fg, 'total_budget': 0})
            budget_map[fg_id] = {field: 0 for field in currency_fields}

            dept_filters = {'finance_group': fg, 'company': company}
            if filters.get('department'):
                filter_depts = frappe.parse_json(filters.get('department'))
                dept_filters['name'] = ['in', filter_depts]
            departments = frappe.db.get_all('Department', filters=dept_filters , pluck='name')

            for dept in departments:
                dept_name = frappe.db.get_value('Department', dept, 'department_name')
                data.append({'id': dept, 'parent': fg_id, 'indent': 2, 'name': dept_name, 'total_budget': 0})
                budget_map[dept] = {field: 0 for field in currency_fields}

                division_filter = {'department': dept}
                if division:
                    division_filter['name'] = division
                divisions = frappe.get_all('Division', filters=division_filter, pluck='name')

                for div in divisions:
                    division_name = frappe.db.get_value('Division', div, 'division')
                    data.append({'id': div, 'parent': dept, 'indent': 3, 'name': division_name, 'total_budget': 0})
                    budget_map[div] = {field: 0 for field in currency_fields}

                    cost_head = filters.get('cost_head', '')
                    cost_heads = get_cost_heads(div, fiscal_year, cost_category=cost_category, cost_head=cost_head, order_by=sort_by_filter)

                    for ch in cost_heads:
                        ch_id = f'{div}-{ch}'
                        data.append({'id': ch_id, 'parent': div, 'indent': 4, 'name': ch, 'total_budget': 0})
                        budget_map[ch_id] = {field: 0 for field in currency_fields}

                        cost_subhead = filters.get('cost_subhead')
                        cost_subheads = get_cost_subheads(div, ch, fiscal_year, cost_category=cost_category, cost_subhead=cost_subhead, order_by=sort_by_filter)

                        for csh in cost_subheads:
                            csh_id = f'{div}-{ch}-{csh}'
                            cost_details = get_cost_subhead_details(div, ch, csh, fiscal_year)
                            total_budget = cost_details.get('total_budget', 0)
                            row_id = cost_details.get('name', )
                            csh_row = {
                                'id': csh_id,
                                'parent': ch_id,
                                'indent': 5,
                                'name': csh,
                                'cost_category': cost_details.get('cost_category', ''),
                                'account': cost_details.get('account', ''),
                                'total_budget': total_budget
                            }
                            if period != 'Yearly':
                                budget_column_data = get_budget_column_data(period, months_order, row_id)
                                csh_row.update(budget_column_data)
                            data.append(csh_row)

                            # Accumulate child budget into its parent
                            for field in currency_fields:
                                budget_map[ch_id][field] += csh_row.get(field, 0)

                        # Propagate cost head budget to department
                        for field in currency_fields:
                            budget_map[div][field] += budget_map[ch_id][field]

                    # Propagate division budget to departments
                    for field in currency_fields:
                        budget_map[dept][field] += budget_map[div][field]
                # Propagate department budget to finance group
                for field in currency_fields:
                    budget_map[fg_id][field] += budget_map[dept][field]

            # Propagate finance group budget to company
            for field in currency_fields:
                budget_map[abbr][field] += budget_map[fg_id][field]

    # Update budget amounts in the data list
    for row in data:
        row.update(budget_map.get(row['id'], {}))

    return data

def get_cost_heads(division, fiscal_year, cost_category=None, cost_head=None, order_by='DESC'):
    '''
        Method to get Cost Heads based on Fiscal Year and Department
    '''
    query = '''
        SELECT
            DISTINCT ba.cost_head
        FROM
            `tabBudget Account` ba
        JOIN
            `tabBudget` b ON ba.parent = b.name
        WHERE
            b.division = %(division)s AND
            b.fiscal_year = %(fiscal_year)s
    '''
    query_filters = {
        'division': division,
        'fiscal_year': fiscal_year
    }
    if cost_category:
        query += ' AND ba.cost_category = %(cost_category)s'
        query_filters['cost_category'] = cost_category
    if cost_head:
        query += ' AND ba.cost_head = %(cost_head)s'
        query_filters['cost_head'] = cost_head
    query += 'GROUP BY ba.cost_head ORDER BY SUM(ba.budget_amount) {0}'.format(order_by)
    cost_heads = frappe.db.sql(query, query_filters, as_dict=True)
    return [row.cost_head for row in cost_heads]

def get_cost_subheads(division, cost_head, fiscal_year, cost_category=None, cost_subhead=None, order_by='DESC'):
    '''
        Method to get Cost Subeads based on Fiscal Year and Department
    '''
    query = '''
        SELECT
            DISTINCT ba.cost_subhead
        FROM
            `tabBudget Account` ba
        JOIN
            `tabBudget` b ON ba.parent = b.name
        WHERE
            ba.cost_head = %(cost_head)s AND
            b.fiscal_year = %(fiscal_year)s AND
            b.division = %(division)s
    '''
    query_filters = {
        'cost_head':cost_head,
        'fiscal_year':fiscal_year,
        'division':division,
        'order_by': order_by
    }
    if cost_category:
        query += ' AND ba.cost_category = %(cost_category)s'
        query_filters['cost_category'] = cost_category
    if cost_subhead:
        query += ' AND ba.cost_subhead = %(cost_subhead)s'
        query_filters['cost_subhead'] = cost_subhead
    query += 'ORDER BY ba.budget_amount {0}'.format(order_by)
    cost_subheads = frappe.db.sql(query, query_filters, as_dict=True)
    return [row.cost_subhead for row in cost_subheads]

def get_cost_subhead_details(division, cost_head, cost_subhead, fiscal_year):
    subhead_details = {
        'cost_category': '',
        'account': '',
        'total_budget': 0
    }
    query = '''
        SELECT
            ba.name,
            ba.cost_category,
            ba.account,
            ba.budget_amount_inr as total_budget
        FROM
            `tabBudget Account` ba
        JOIN
            `tabBudget` b ON ba.parent = b.name
        WHERE
            b.division = %(division)s AND
            b.fiscal_year = %(fiscal_year)s AND
            ba.cost_head = %(cost_head)s AND
            ba.cost_subhead = %(cost_subhead)s
    '''
    query_params = {
        'division':division,
        'fiscal_year':fiscal_year,
        'cost_head':cost_head,
        'cost_subhead':cost_subhead
    }

    details = frappe.db.sql(query, query_params, as_dict=True)
    if details:
        subhead_details = details[0]
    return subhead_details

def get_budget_column_data(period, months_order, row_id):
    '''
        Get Columnar data specif to period
    '''
    budget_column_data = {}
    if frappe.db.exists('Budget Account', row_id):
        data = frappe.db.get_value('Budget Account', row_id, fieldname=months_order, as_dict=True)
        if period == 'Monthly':
            for month in months_order:
                label = 'budget_({0})'.format(month[0:3])
                budget_column_data[label] = data.get(month)
        if period == 'Quarterly':
            total = 0
            for i, month in enumerate(months_order):
                total += data.get(month)
                if i in [2, 5, 8, 11]:
                    label = 'budget_({0}_{1})'.format(months_order[i-2][0:3], month[0:3])
                    budget_column_data[label] = total
                    total = 0
        if period == 'Half-Yearly':
            total = 0
            for i, month in enumerate(months_order):
                total += data.get(month)
                if i in [5, 11]:
                    label = 'budget_({0}_{1})'.format(months_order[i-5][0:3], month[0:3])
                    budget_column_data[label] = total
                    total = 0
    return budget_column_data