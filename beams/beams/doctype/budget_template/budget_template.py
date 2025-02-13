# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BudgetTemplate(Document):

    def set_default_account(self):
        if not hasattr(self, "budget_template_item") or not self.budget_template_item:
            return

        for item in self.budget_template_item:
            if not item.cost_sub_head or not self.company:
                item.account = ""
                continue

            cost_subhead_doc = frappe.get_doc("Cost Subhead", item.cost_sub_head)

            if cost_subhead_doc.accounts:
                account_found = next((acc for acc in cost_subhead_doc.accounts if acc.company == self.company), None)
                item.account = account_found.default_account if account_found else ""
            else:
                item.account = ""

    def before_save(self):
        self.set_default_account()
