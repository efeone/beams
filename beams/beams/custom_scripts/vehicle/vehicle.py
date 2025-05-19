import frappe
from frappe.utils import today, add_days, formatdate, getdate
from datetime import datetime
from frappe.utils.user import get_users_with_role
from frappe.email.doctype.email_account.email_account import EmailAccount
from frappe.utils import nowdate, nowtime

@frappe.whitelist()
def send_vehicle_document_reminders():

    """
    Sends email reminders for vehicle document expiry.

    This method checks all vehicles and their associated documents to identify:
    1. Documents that are due for a reminder based on the `reminder_before` field.
    2.Documents that are overdue (past their expiry date).
    It compiles the details into an HTML table and sends an email to all users with the "Admin" role.
    Email includes:
        - License Plate
        - Model
        - Document Name
        - Expiry Date

    Emails are sent only if there are documents that meet the criteria for reminders.
    """
    # Fetch all Vehicle documents
    vehicles = frappe.get_all("Vehicle", fields=["name", "license_plate", "model"])

    for vehicle in vehicles:
        # Get the Vehicle document with child table data
        vehicle_doc = frappe.get_doc("Vehicle", vehicle["name"])

        reminder_details = []  # Collect reminder details for the email

        for doc in vehicle_doc.vehicle_documents:
            if doc.expiry_date:
                # Fetch the linked Vehicle Document to get the reminder_before field
                vehicle_document = frappe.get_doc("Vehicle Document", doc.document)
                reminder_before = vehicle_document.reminder_before or 0  # Default to 0 if not set

                # Calculate the reminder date
                reminder_date = add_days(doc.expiry_date, -reminder_before)
                # Check if today matches the reminder date or the document is overdue
                if getdate(today()) == reminder_date or doc.expiry_date <= getdate(today()):
                    # Add details to the list
                    reminder_details.append(
                        f"""
                        <tr>
                            <td>{vehicle['license_plate']}</td>
                            <td>{vehicle['model']}</td>
                            <td>{doc.document}</td>
                            <td>{doc.expiry_date}</td>
                        </tr>
                        """
                    )

        if reminder_details:
            # Email content
            email_content = f"""
            <h3>Vehicle Document Expiry/Reminder</h3>
            <p>The following vehicle documents are overdue or expiring soon:</p>
            <table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>License Plate</th>
                        <th>Model</th>
                        <th>Document</th>
                        <th>Expiry Date</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(reminder_details)}
                </tbody>
            </table>
            """
            
            # Get admin users
            email_recipients = get_users_with_role("Admin")


            # Send email to all admin users
            if email_recipients:
                frappe.sendmail(
                    recipients=email_recipients,
                    subject="Vehicle Document Expiry Reminder",
                    message=email_content,
                )


def create_vehicle_documents_log(doc, method):
    """Log changes to Vehicle Documents in a single log per Vehicle, appending changed rows without duplicates."""

    prev_docs = doc.get_doc_before_save().get("vehicle_documents") if doc.get_doc_before_save() else []
    curr_docs = doc.get("vehicle_documents") or []
    log_name = frappe.db.get_value("Vehicle Documents Log", {"vehicle": doc.name}, "name")
    log = frappe.get_doc("Vehicle Documents Log", log_name) if log_name else frappe.new_doc("Vehicle Documents Log")
    if not log_name:
        log.update({
            "vehicle": doc.name,
            "license_plate": doc.license_plate,
            "make": doc.make,
            "model": doc.model
        })
    prev_dict = {row.name: row.as_dict() for row in prev_docs}
    curr_dict = {row.name: row.as_dict() for row in curr_docs}
    changed = False
    def is_duplicate_in_log(log, row):
        for log_row in log.get("vehicle_documents", []):
            if (log_row.document == row.document and
                log_row.reference_no == row.reference_no and
                log_row.expiry_date == row.expiry_date and
                log_row.remarks == row.remarks):
                return True
        return False
    for row_name, row in curr_dict.items():
        if row_name not in prev_dict:
            row_data = {
                "document": row.document,
                "reference_no": row.reference_no,
                "expiry_date": row.expiry_date,
                "remarks": row.remarks
            }
            if not is_duplicate_in_log(log, row):
                log.append("vehicle_documents", row_data)
                changed = True
    if changed or not log_name:
        log.save(ignore_permissions=True)
