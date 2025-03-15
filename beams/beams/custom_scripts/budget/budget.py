import frappe

def update_total_amount(doc, method):
    total = sum([row.budget_amount for row in doc.get("accounts") if row.budget_amount])
    doc.total_amount = total

def populate_og_accounts(doc, method=None):
    doc.accounts = []
    for row in doc.get("budget_accounts_custom"):
        doc.append("accounts", row)
    for row in doc.get("budget_accounts_hr"):
        doc.append("accounts", row)
