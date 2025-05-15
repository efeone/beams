import frappe


@frappe.whitelist()
def notify_stock_managers(doc=None, method=None):
    """
    Notifies all users with 'Stock Manager' role via email after a Material Request is created.
    Can be called from hooks or API.
    """
    if isinstance(doc, str):
        doc = frappe.get_doc("Material Request", doc)

    # Fetch users with "Stock Manager" role and their email addresses
    recipients = [
        user.email for user in frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "user_type": "System User"
            },
            fields=["name", "email"]
        ) if any(role in frappe.get_roles(user.name) for role in ["Stock Manager", "Admin"])
    ]

    if not recipients:
        return

    subject = f"📦 New Material Request: {doc.name}"
    message = frappe.render_template(
        """
        <p>Hello,</p>
        <p>A new <strong>Material Request</strong> has been created:</p>
        <ul>
            <li><strong>Name:</strong> {{ doc.name }}</li>
            <li><strong>Type:</strong> {{ doc.material_request_type }}</li>
            <li><strong>Date:</strong> {{ doc.transaction_date }}</li>
            <li><strong>Requested By:</strong> {{ doc.owner }}</li>
        </ul>
        <p>Please log in to review it.</p>
        """,
        {"doc": doc}
    )

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        delayed=False,
        reference_doctype="Material Request",
        reference_name=doc.name
    )
