# import frappe
# from frappe.utils.user import get_users_with_role


# @frappe.whitelist()
# def notify_stock_managers(doc, method=None):
#     if isinstance(doc, str):
#         doc = frappe.get_doc("Material Request", doc)

#     recipients = frappe.get_users_with_role("Stock Manager")
#     recipients = [r for r in recipients if r not in ("Administrator", "Guest")]

#     if not recipients:
#         return

#     def get_items_table():
#         if not doc.items:
#             return "<p>No items listed.</p>"

#         rows = ""
#         for item in doc.items:
#             rows += f"""
#             <tr>
#                 <td>{item.item_code}</td>
#                 <td>{item.item_name or ''}</td>
#                 <td>{item.qty}</td>
#                 <td>{item.schedule_date or ''}</td>
#             </tr>
#             """
#         return f"""
#         <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%;">
#             <thead>
#                 <tr>
#                     <th>Item Code</th>
#                     <th>Item Name</th>
#                     <th>Qty</th>
#                     <th>Schedule Date</th>
#                 </tr>
#             </thead>
#             <tbody>
#                 {rows}
#             </tbody>
#         </table>
#         """

#     subject = f"New Material Request Created: {doc.name}"

#     message = f"""
#     <p>Dear Stock Manager,</p>

#     <p>A new <b>Material Request</b> has been created:</p>

#     <ul>
#         <li><b>Request Type:</b> {doc.material_request_type}</li>
#         <li><b>Requested By:</b> {doc.owner}</li>
#         <li><b>Required Date:</b> {doc.schedule_date or 'N/A'}</li>
#         <li><b>Company:</b> {doc.company}</li>
#         <li><b>Project:</b> {doc.project or 'N/A'}</li>
#     </ul>

#     <h4>Items:</h4>
#     {get_items_table()}

#     <p>Regards,<br>ERP System</p>
#     """

#     frappe.sendmail(
#         recipients=recipients,
#         subject=subject,
#         message=message
#     )
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
        ) if "Stock Manager" in frappe.get_roles(user.name)
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
