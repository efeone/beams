

import frappe
from frappe.model.document import Document
import os
import io
import json
from pyqrcode import create


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
