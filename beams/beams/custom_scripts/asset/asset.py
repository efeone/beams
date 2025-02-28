# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
import io
import json
from pyqrcode import create
from frappe.utils import getdate, add_months, nowdate


@frappe.whitelist()
def generate_asset_qr(doc,method = None):
    qr_code = doc.get("qr_code")
    if qr_code and frappe.db.exists({"doctype": "File", "file_url": qr_code}):
        return
    doc_url = get_si_json(doc)
    qr_image = io.BytesIO()
    url = create(doc_url, error="L")
    url.png(qr_image, scale=4, quiet_zone=1)
    name = frappe.generate_hash(doc.name, 5)
    filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": filename,
            "is_private": 0,
            "content": qr_image.getvalue(),
            "attached_to_doctype": doc.get("doctype"),
            "attached_to_name": doc.get("name"),
            "attached_to_field": "qr_code",
        }
    )
    _file.save()
    doc.db_set("qr_code", _file.file_url)

def get_si_json(doc):
    essential_fields = [
        "item_code",
        "asset_name",
        "location",
        "asset_owner",
    ]
    item_data = {}
    for field in essential_fields:
        value = doc.get(field)
        item_data[field] = value
    json_data = json.dumps(item_data, indent=4)
    return json_data

@frappe.whitelist()
def asset_notifications():
    """Send asset notifications based on the selected frequency and start month."""
    today = getdate(nowdate())
    current_month = today.month
    current_year = today.year
    beams_settings = frappe.get_single("BEAMS Admin Settings")
    default_notification_enabled = beams_settings.asset_audit_notification
    default_frequency = beams_settings.notifcation_frequency
    default_email_template = beams_settings.notification_template
    default_start_month = beams_settings.start_notification_from
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    global_start_month_num = month_map.get(default_start_month, None)
    assets = frappe.get_all("Asset", fields=["name", "item_code", "custodian"])
    for asset in assets:
        item = frappe.db.get_value(
            "Item", asset.item_code,
            ["item_audit_notification", "item_notification_frequency", "item_notification_template", "start_notification_from"],
            as_dict=True
        ) if asset.item_code else {}
        notify_enabled = item.get("item_audit_notification") or default_notification_enabled
        frequency = item.get("item_notification_frequency") or default_frequency
        email_template = item.get("item_notification_template") or default_email_template
        item_start_month = item.get("start_notification_from")
        item_start_month_num = month_map.get(item_start_month, None)
        if not notify_enabled or not email_template:
            continue
        start_month_num = item_start_month_num if item_start_month_num else global_start_month_num
        if not start_month_num:
            continue
        send_notification = False
        if frequency == "Monthly":
            send_notification = True
        elif frequency == "Trimonthly":
            send_notification = (current_month - start_month_num) % 3 == 0 if current_month >= start_month_num else (start_month_num - current_month) % 3 == 0
        elif frequency == "Quarterly":
            send_notification = (current_month - start_month_num) % 4 == 0 if current_month >= start_month_num else (start_month_num - current_month) % 4 == 0
        elif frequency == "Half Yearly":
            send_notification = (current_month - start_month_num) % 6 == 0 if current_month >= start_month_num else (start_month_num - current_month) % 6 == 0
        elif frequency == "Yearly":
            send_notification = current_month == start_month_num
        if not send_notification:
            continue
        recipient = frappe.db.get_value("Employee", asset.custodian, "user_id")
        if not recipient:
            continue
        email_template_doc = frappe.get_doc("Email Template", email_template)
        message = frappe.render_template(email_template_doc.response, {"asset": asset})
        frappe.sendmail(
            recipients=[recipient],
            subject=email_template_doc.subject,
            message=message
        )
