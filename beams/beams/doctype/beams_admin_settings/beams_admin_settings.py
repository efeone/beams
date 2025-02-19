import frappe
from frappe.utils import nowdate, add_days
from frappe.model.document import Document
from frappe.email.doctype.email_account.email_account import EmailAccount

class BEAMSAdminSettings(Document):
    pass


@frappe.whitelist()
def send_asset_audit_reminder():
    '''
    If Asset Auditing Notification is checked, Send Notification to users with "Technical Store Head" role and Current asset owner.
    '''

    settings = frappe.get_single("BEAMS Admin Settings")

    if settings.asset_auditing_notificaton:
        notify_days = settings.notify_after
        template_name = settings.asset_auditing_notification_template

        if not notify_days or not template_name:
            frappe.log_error("Asset Audit Notification: Configuration missing", "Asset Auditing")
            return

        # Get Email Template
        email_template = frappe.get_doc("Email Template", template_name)
        if not email_template:
            frappe.log_error("Asset Audit Notification: Email Template not found", "Asset Auditing")
            return

        audit_due_date = add_days(nowdate(), -notify_days)

        assets = frappe.get_all("Asset Auditing",
            filters={"posting_date": ["<=", audit_due_date]},
            fields=["asset", "posting_date"])

        asset_names = list(set([a["asset"] for a in assets]))

        if asset_names:
            asset_details = frappe.get_all("Asset",
                filters={"name": ["in", asset_names]},
                fields=["name", "asset_name", "asset_owner", "company"])

            for asset in asset_details:
                recipients = get_asset_notification_recipients(asset)
                if recipients:
                    subject = f"Asset Audit Reminder: {asset.asset_name}"
                    message = f"""
                    <p>Reminder : The asset <b>{asset.asset_name}</b> was last audited on {next(a['posting_date'] for a in assets if a['asset'] == asset['name'])}.<br>
                    Please ensure it is audited again.</p>
                    <p>Thank you,<br>
                    Technical Store Department</p>
                    """
                    frappe.sendmail(
                    recipients=recipients,
                    subject=subject,
                    message=message,
                    )

                    send_inapp_notification(recipients, subject, message)


def get_asset_notification_recipients(asset):
    recipients = set()

    # Get Users with "Technical Store Head" Role
    it_users = frappe.get_all("User",
        filters={"enabled": 1},
        fields=["name", "email"])

    for user in it_users:
        if frappe.get_all("Has Role", filters={"parent": user.name, "role": "Technical Store Head"}):
            recipients.add(user.email)

    # Add Asset Owner
    if asset.asset_owner:
        recipients.add(asset.asset_owner)

    return list(recipients)


def send_inapp_notification(recipients, subject, message):
    '''
    Create in-app notifications for recipients
    '''
    for email in recipients:
        user = frappe.get_value("User", {"email": email}, "name")

        if user:
            notification = frappe.get_doc({
                "doctype": "Notification Log",
                "subject": subject,
                "email_content": message,
                "for_user": user,
                "type": "Alert"
            })
            notification.insert(ignore_permissions=True)

            # Publish Real-time Notification
            frappe.publish_realtime(event="msgprint",
                message=message,
                user=user)
