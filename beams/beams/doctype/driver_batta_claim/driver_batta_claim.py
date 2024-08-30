# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DriverBattaClaim(Document):
    def on_submit(self):
        if self.workflow_state == 'Approved':
            self.create_purchase_invoice_from_driver_batta_claim()

    def create_purchase_invoice_from_driver_batta_claim(self):
        """
            Creation of Purchase Invoice On The Approval Of the Driver Batta Claim.
        """
        purchase_invoice = frappe.new_doc('Purchase Invoice')
        driver = frappe.get_doc("Driver", self.driver)
        purchase_invoice.supplier = driver.transporter
        purchase_invoice.posting_date = frappe.utils.nowdate()
        purchase_invoice.append('items', {
            'item_code': 'Driver Batta Claim',  # Static item code
            'rate': self.total_driver_batta,  # Assuming total_driver_batta is the rate
            'qty': 1  # Adjust quantity as needed
        })

        purchase_invoice.insert()
        purchase_invoice.submit()
