import frappe
from frappe.utils import get_url_to_form

def notify_expense_approver_on_creation(doc, method=None):
    '''
    Notifies the expense approver (via email and ToDo) when a new Expense Claim is created.
    Triggered via hooks.py using after_insert.
    '''

    approver = doc.expense_approver or frappe.db.get_value("Employee", doc.employee, "expense_approver")


    if not frappe.db.exists("ToDo", {
        "reference_type": "Expense Claim",
        "reference_name": doc.name,
        "owner": approver
    }):
        frappe.get_doc({
            "doctype": "ToDo",
            "owner": approver,
            "description": f"Please review Expense Claim {doc.name} submitted by {doc.employee}.",
            "reference_type": "Expense Claim",
            "reference_name": doc.name,
            "priority": "Medium"
        }).insert(ignore_permissions=True)

    subject = f"New Expense Claim Submitted: {doc.name}"
    message = f'''
        Dear Approver,<br><br>
        A new Expense Claim <b>{doc.name}</b> has been submitted by <b>{doc.employee}</b>.<br>
        <a href="{get_url_to_form('Expense Claim', doc.name)}">Click here</a> to review the claim.<br><br>
        Regards,<br>
        ERP System
    '''

    frappe.sendmail(
        recipients=[approver],
        subject=subject,
        message=message
    )
