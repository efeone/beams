import frappe

fields_to_remove = [
    {
        'dt':'Customer',
        'fieldname':'albatross_customer_id'
    }
]

def execute():
    for field in fields_to_remove:
        if frappe.db.exists('Custom Field', field):
            frappe.db.delete('Custom Field', field)
    frappe.db.commit()
