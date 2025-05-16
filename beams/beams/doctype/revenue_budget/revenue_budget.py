# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RevenueBudget(Document):
    def before_save(self):
        self.calculate_total_amount()

    def validate(self):
        self.convert_currency()

    def calculate_total_amount(self):
        total = sum([row.revenue_amount for row in self.get("revenue_accounts") if row.revenue_amount])
        self.total_amount = total

    def convert_currency(self):
        """Convert Revenue amounts for non-INR companies"""
        company_currency = frappe.db.get_value("Company", self.company, "default_currency")
        exchange_rate = 1

        if company_currency != "INR":
            exchange_rate = frappe.db.get_value("Company", self.company, "exchange_rate_to_inr")
            if not exchange_rate:
                frappe.throw(
                    f"Please set Exchange Rate from <b>{company_currency}</b> to <b>INR</b> for <b>{self.company}</b>",
                    title="Message",
                )

        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]

        def apply_conversion(row):
            """Apply exchange rate conversion to a revenue row"""
            row.revenue_amount_inr = row.revenue_amount * exchange_rate
            for month in months:
                setattr(row, f"{month}_inr", (getattr(row, month, 0) or 0) * exchange_rate)

        for row in self.revenue_accounts:
            apply_conversion(row)

@frappe.whitelist()
def get_revenue_template(revenue_category, company):
    """Get Revenue Template based on Revenue category and selected Company"""
    template = frappe.db.get_value(
        "Revenue Template",
        {"revenue_category": revenue_category, "company": company},
        "name"
    )
    return template
