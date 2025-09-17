# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CourierLog(Document):

    def validate(self):
        self.notify_recipient()

    def notify_recipient(self):
        for record in self.recipients:
            if record.recepient and record.delivered and not record.received:
                user = frappe.db.get_value("Employee", record.recepient, "user_id")
                if user:
                    self.create_system_notification(user)

    def create_system_notification(self, user):
        """Create notification for the user"""
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Courier Delivered: {self.name}",
            "email_content": f"A courier has been marked delivered under log <b>{self.name}</b>. Please confirm receipt.",
            "for_user": user,
            "type": "Alert",
            "document_type": "Courier Log",
            "document_name": self.name
        }).insert(ignore_permissions=True)
