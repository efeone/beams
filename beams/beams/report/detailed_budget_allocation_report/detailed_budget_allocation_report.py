import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    return [
        {"fieldname": "name", "label": "", "fieldtype": "Data", "width": 500},
        {"fieldname": "cost_category", "label": "Cost Category", "fieldtype": "Data", "width": 200},
        {"fieldname": "account", "label": "Account", "fieldtype": "Data", "width": 200},
        {"fieldname": "budget_amount", "label": "Budget Amount", "fieldtype": "Currency", "width": 200},
    ]

def get_data():
    data = []

    def add_node(name, parent, indent, cost_category=None, account=None, budget_amount=0):
        '''
            Method to bring parent child relation
        '''
        data.append({
            "name": name,
            "parent": parent,
            "indent": indent,
            "budget_amount": budget_amount
        })

    # Fetch all companies
    companies = frappe.get_all("Company", pluck='name')
    for company in companies:
        add_node(name=company, parent="", indent=0)

        # Fetch Finance Groups
        finance_groups = frappe.get_all("Finance Group", pluck='name')
        for fg in finance_groups:
            add_node(name=fg, parent=company, indent=1)

            # Fetch Departments under Finance Group
            departments = frappe.get_all("Department", filters={"finance_group": fg, "company": company }, pluck='name')
            for dept in departments:
                add_node(name=dept, parent=fg, indent=2)

                # Fetch Cost Heads
                cost_heads = get_cost_heads(dept)
                for ch in cost_heads:
                    add_node(name=ch, parent=dept, indent=3)

                    # Fetch Cost Subheads under Cost Head
                    cost_subheads = frappe.get_all("Cost Subhead", filters={"cost_head": ch}, pluck='name')
                    for csh in cost_subheads:
                        cost_head_deatils = get_cost_subhead_details(dept, csh)
                        cost_category = cost_head_deatils.get('cost_category', '')
                        account = cost_head_deatils.get('account', '')
                        amount = cost_head_deatils.get('budget_amount', 0)
                        add_node(name=csh, parent=ch, indent=4, cost_category=cost_category, account=account, budget_amount=amount)

    return data

def get_cost_heads(department):
    '''
        Method to get Cost Heads for a Department, based on existing budget
    '''
    if not department:
        return []
    
    cost_heads = frappe.db.sql(
        """
            SELECT
                DISTINCT ba.cost_head 
            FROM
                `tabBudget Account` ba
            JOIN
                `tabBudget` b ON ba.parent = b.name
            WHERE
                b.department = %s
        """, (department,), as_dict=True)
    
    return [row.cost_head for row in cost_heads]

def get_cost_subhead_details(department, cost_subhead):
    '''
        Method to get details of a cost subhead
    '''
    details = frappe.db.sql(
        """
            SELECT
                *
            FROM
                `tabBudget Account` ba
            JOIN
                `tabBudget` b ON ba.parent = b.name
            WHERE
                b.department = %(department)s and
                ba.cost_subhead = %(cost_subhead)s
        """, { 'department':department, 'cost_subhead':cost_subhead }, as_dict=True)
    if details:
        return details[0]
    return {}