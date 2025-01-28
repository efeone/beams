import frappe
from frappe.utils import flt

@frappe.whitelist()
def create_journal_entry(doc, method):
    """
    Create Journal Entry for Provident Fund (PF) deduction upon submission of Salary Slip.
    """

    pf_deduction = None
    for deduction in doc.deductions:
        if deduction.salary_component == "Provident Fund":
            pf_deduction = deduction
            break

    if not pf_deduction:
        return

    pf_amount = pf_deduction.amount

    # Fetch PF Expense Account from Payroll Settings
    pf_expense_account = frappe.db.get_single_value("Payroll Settings", "pf_expense_account")
    if not pf_expense_account:
        frappe.throw(
            title="Missing Configuration",
            msg="Please configure the PF Expense Account in Payroll Settings."
        )

    # Fetch PF Payable Account from the Salary Component for the given company
    pf_payable_account = frappe.db.get_value(
        "Salary Component Account",
        filters={
            "parentfield": "accounts",
            "parenttype": "Salary Component",
            "parent": "Provident Fund",
            "company": doc.company
        },
        fieldname="account"
    )
    if not pf_payable_account:
        frappe.throw(
            title="Missing Account",
            msg=f"No PF Payable Account found for the company {doc.company}. Please check the Salary Component configuration."
        )

    # Step 4: Create the Journal Entry
    journal_entry = frappe.new_doc("Journal Entry")
    journal_entry.voucher_type = "Journal Entry"
    journal_entry.company = doc.company
    journal_entry.posting_date = doc.posting_date
    journal_entry.reference_doctype = "Salary Slip"
    journal_entry.reference_name = doc.name

    # Add debit entry for PF Expense
    journal_entry.append("accounts", {
        "account": pf_expense_account,
        "debit_in_account_currency": pf_amount,
    })

    # Add credit entry for PF Payable
    journal_entry.append("accounts", {
        "account": pf_payable_account,
        "credit_in_account_currency": pf_amount,
    })

    # Insert and Submit the Journal Entry
    journal_entry.insert()
    journal_entry.submit()
