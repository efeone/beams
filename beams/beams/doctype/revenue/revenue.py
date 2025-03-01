# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Revenue(Document):
    def before_naming(self):
        self.naming_series = f"{{{frappe.scrub(self.revenue_against)}}}./.{self.fiscal_year}/.###"

    def before_save(self):
        self.calculate_total_amount()

    def calculate_total_amount(self):
        total = sum([row.revenue_amount for row in self.get("revenue_accounts") if row.revenue_amount])
        self.total_amount = total
