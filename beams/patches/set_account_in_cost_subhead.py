import frappe

def execute():
    cost_subheads = frappe.get_all('Cost Subhead', pluck='name')
    default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
    for subhead in cost_subheads:
        cost_subhead_doc = frappe.get_doc('Cost Subhead', subhead)
        cost_subhead_doc.append('accounts', {
            'company': default_company,
            'default_account': cost_subhead_doc.account
        })
        cost_subhead_doc.flags.ignore_mandatory = True
        cost_subhead_doc.save()
    frappe.db.commit()
