import frappe

@frappe.whitelist()
def create_petty_cash_request(voucher_entry_name, bureau, mode_of_payment, account, requested_amount):
    """Create a Petty Cash Request linked to a Voucher Entry"""

    # Get Employee ID based on logged-in user
    employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")

    # Create a new Petty Cash Request document
    petty_cash = frappe.get_doc({
        "doctype": "Petty Cash Request",
        "bureau": bureau,
        "petty_cash_account": mode_of_payment,
        "account": account,
        "requested_amount": requested_amount,
        "reference_voucher": voucher_entry_name,
        "employee": employee
    })

    petty_cash.insert(ignore_permissions=True)
    petty_cash.submit()
    frappe.db.commit()

    return {"status": "success", "message": "Petty Cash Request Created Successfully!", "docname": petty_cash.name}
