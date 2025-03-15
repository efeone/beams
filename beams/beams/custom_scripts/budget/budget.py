import frappe


def beams_budget_validate(doc, method=None):
    """method runs custom validations for budget doctype"""
    update_total_amount(doc, method)
    convert_currency(doc, method)


def update_total_amount(doc, method):
    total = sum([row.budget_amount for row in doc.get("accounts") if row.budget_amount])
    doc.total_amount = total


def populate_og_accounts(doc, method=None):
    doc.accounts = []
    for row in doc.budget_accounts_custom:
        accounts_row = row.as_dict()
        accounts_row.pop('name')
        accounts_row.pop('idx')
        doc.append("accounts", accounts_row)
    for row in doc.budget_accounts_hr:
        accounts_row = row.as_dict()
        accounts_row.pop('name')
        accounts_row.pop('idx')
        doc.append("accounts", accounts_row)


def convert_currency(doc, method):
    """Convert budget amounts for non-INR companies"""
    company_currency = frappe.db.get_value("Company", doc.company, "default_currency")
    if company_currency == "INR":
        return

    exchange_rate = frappe.db.get_value("Company", doc.company, "exchange_rate_to_inr")
    if not exchange_rate:
        frappe.throw(
            f"Please set Exchange Rate from <b>{company_currency}</b> to <b>INR</b> for <b>{doc.company}</b>",
            title="Message",
        )

    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]

    def apply_conversion(row):
        """Apply exchange rate conversion to a budget row"""
        row.budget_amount_inr = row.budget_amount * exchange_rate
        for month in months:
            setattr(row, f"{month}_inr", getattr(row, month, 0) * exchange_rate)

    for row in (*doc.accounts, *doc.budget_accounts_custom):
        apply_conversion(row)

