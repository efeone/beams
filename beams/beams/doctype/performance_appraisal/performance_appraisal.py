# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PerformanceAppraisal(Document):
	pass

@frappe.whitelist()
def fetch_kra_data(template_name):
    '''Fetch KRA data from the Goals child table of the given Appraisal Template.'''
    # Get the Appraisal Template document
    template = frappe.get_doc("Appraisal Template", template_name)

    # Extract KRA data from the Goals child table
    kra_list = [goal.key_result_area for goal in template.goals]

    return kra_list
