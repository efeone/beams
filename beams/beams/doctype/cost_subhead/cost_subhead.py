# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CostSubhead(Document):
	pass

@frappe.whitelist()
def update_budget_templates(cost_subhead):
    cost_subhead_doc = frappe.get_doc("Cost Subhead", cost_subhead)

    budget_templates = frappe.get_all("Budget Template Item",
        filters={"cost_sub_head": cost_subhead}, fields=["parent"])

    for budget in {bt["parent"] for bt in budget_templates}:
        budget_doc = frappe.get_doc("Budget Template", budget)

        for item in budget_doc.get("budget_template_item", []):
            if item.cost_sub_head == cost_subhead:
                item.account = next(
                    (acc.default_account for acc in cost_subhead_doc.accounts if acc.company == budget_doc.company),
                    item.account
                )

        budget_doc.save()

    return "Success"
