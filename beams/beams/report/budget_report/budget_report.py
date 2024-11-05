# # # Copyright (c) 2024, efeone and contributors
# # # For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from decimal import Decimal, ROUND_DOWN

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": _("Budget"), "fieldname": "budget_link", "fieldtype": "Link", "options": "Budget", "width": 230},
        {"label": _("Cost Description"), "fieldname": "cost_description", "fieldtype": "Data", "width": 230},
        {"label": _("Cost Sub Head"), "fieldname": "cost_subhead", "fieldtype": "Data", "width": 230},
        {"label": _("Cost Category"), "fieldname": "cost_category", "fieldtype": "Data", "width": 170},
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 230},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 170},
        {"label": _("Fiscal Year"), "fieldname": "fiscal_year", "fieldtype": "Data", "width": 100},
        {"label": _("Total Budget Amount"), "fieldname": "budget_amount", "fieldtype": "Currency", "width": 120},
    ]

    # Generate month columns based on fiscal year dates
    if filters.get("fiscal_year"):
        fiscal_year = filters.get("fiscal_year")
        fiscal_year_data = frappe.get_doc("Fiscal Year", fiscal_year)
        year_start_date = fiscal_year_data.year_start_date
        year_end_date = fiscal_year_data.year_end_date
        month_labels = generate_month_labels(year_start_date, year_end_date)

        for month in month_labels:
            columns.append({"label": month, "fieldname": month.lower(), "fieldtype": "Currency", "width": 150})

    return columns

def generate_month_labels(year_start_date, year_end_date):
    """Generate month labels based on the fiscal year start and end dates."""
    start = year_start_date
    end = year_end_date
    month_labels = []

    while start <= end:
        month_labels.append(start.strftime("%B"))
        # Move to the next month
        if start.month == 12:
            start = start.replace(year=start.year + 1, month=1)
        else:
            start = start.replace(month=start.month + 1)

    return month_labels

def get_data(filters):
    """Fetch budget data along with monthly allocations."""
    query = """
        SELECT
            b.name AS budget_link,
            a.cost_description,
            a.cost_subhead,
            b.department,
            a.cost_category,
            a.account,
            b.fiscal_year,
            a.budget_amount,
            b.monthly_distribution
        FROM
            `tabBudget` AS b
        LEFT JOIN
            `tabBudget Account` AS a ON a.parent = b.name
        WHERE
            b.docstatus = 1
    """

    if filters.get("fiscal_year"):
        query += " AND b.fiscal_year = %(fiscal_year)s"
    if filters.get("department"):
        query += " AND b.department = %(department)s"

    data = frappe.db.sql(query, filters, as_dict=True)
    result_data = []

    last_budget = None
    for row in data:
        # Clear duplicate budget_link values
        if row["budget_link"] == last_budget:
            row["budget_link"] = ""
        else:
            last_budget = row["budget_link"]

        # Fetch the monthly distribution linked to the budget
        monthly_distribution = row["monthly_distribution"]

        month_allocation = {month.lower(): flt(0) for month in generate_month_labels(
            frappe.db.get_value("Fiscal Year", row["fiscal_year"], "year_start_date"),
            frappe.db.get_value("Fiscal Year", row["fiscal_year"], "year_end_date"))}

        # If a monthly distribution is found, get the percentage allocations for the current account
        if monthly_distribution:
            percentages = frappe.get_all(
                "Monthly Distribution Percentage",
                filters={"parent": monthly_distribution},
                fields=["month", "percentage_allocation"]
            )

            # Calculate allocated amount for each percentage and assign to the corresponding month column
            for percentage in percentages:
                month_column = percentage.month.lower()
                budget_amount = Decimal(row.get("budget_amount", 0))
                allocation_percentage = Decimal(percentage.percentage_allocation)
                allocated_amount = (budget_amount * allocation_percentage) / Decimal(100)
                month_allocation[month_column] = allocated_amount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)


        result_data.append({
            "budget_link": row["budget_link"],
            "cost_description": row["cost_description"],
            "cost_subhead": row["cost_subhead"],
            "cost_category": row["cost_category"],
            "account": row["account"],
            "department": row["department"],
            "fiscal_year": row["fiscal_year"],
            "budget_amount": row["budget_amount"],
            **month_allocation
        })

    return result_data
