import frappe

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
