# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import nowdate, add_days
from frappe.model.document import Document
from frappe.utils.user import get_users_with_role


class BEAMSAdminSettings(Document):
    pass

@frappe.whitelist()
def send_asset_audit_reminder():
    '''
    If Asset Auditing Notification is checked, Send Notification to users with "Technical Store Head" role and Current asset owner.
    '''
    settings = frappe.get_single("BEAMS Admin Settings")

    if not settings or not settings.asset_auditing_notification:
        return

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

    asset_names = list(set(a["asset"] for a in assets if "asset" in a))

    if asset_names:
        asset_details = frappe.get_all("Asset",
            filters={"name": ["in", asset_names]},
            fields=["name", "asset_name", "asset_owner", "company"])

        for asset in asset_details:
            recipients = get_asset_notification_recipients(asset)
            if recipients:
                subject = f"Asset Audit Reminder: {asset['asset_name']}"
                last_audited = next((a['posting_date'] for a in assets if a['asset'] == asset['name']), "Unknown Date")
                message = f"""
                <p>Reminder: The asset <b>{asset['asset_name']}</b> was last audited on {last_audited}.<br>
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
    technical_store_users = get_users_with_role("Technical Store Head")
    if technical_store_users:
        recipients.update(technical_store_users)

    # Add Asset Owner
    if asset.get("asset_owner"):
        recipients.add(asset["asset_owner"])

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
