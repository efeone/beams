import frappe

def execute():
    budget_templates = frappe.get_all('Budget Template', pluck='name')
    default_company = frappe.db.get_single_value('Global Defaults', 'default_company')

    for budget_template in budget_templates:
        budget_template_doc = frappe.get_doc('Budget Template', budget_template)
        if not budget_template_doc.company:
            budget_template_doc.company = default_company
            budget_template_doc.flags.ignore_mandatory = True
            budget_template_doc.save()
    frappe.db.commit()
