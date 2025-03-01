import frappe

def update_total_amount(doc, method):
    total = sum([row.budget_amount for row in doc.get("accounts") if row.budget_amount])
    doc.total_amount = total
