# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Division(Document):
    def validate(self):
        if self.cost_center:
            divisions = frappe.get_list('Division', filters={'cost_center': self.cost_center}, fields=['name'])

            if divisions:
                division_name = divisions[0].get('name')
                frappe.throw(
                    _("The selected Cost Center is already assigned to Division: {0}. Please choose a different one.").format(division_name)
                )

@frappe.whitelist()
def get_used_cost_centers():
    """
    Fetch divisions that have a cost center set.
    Returns a list of used cost centers.
    """
    # Fetch divisions with a cost center set
    divisions = frappe.db.get_list(
        'Division',
        fields=['cost_center'],
        filters={'cost_center': ['is', 'set']}
    )

    # Extract the cost centers from the result
    used_cost_centers = [division['cost_center'] for division in divisions]

    return used_cost_centers
