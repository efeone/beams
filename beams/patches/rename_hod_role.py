import frappe

def execute():
    if frappe.db.exists("Role", 'Hod'):
        if frappe.db.exists("Role", 'Hod') == 'Hod':
            frappe.rename_doc("Role", 'Hod', 'HOD')
            print("Role `Hod` renamed to `HOD`")
            frappe.db.commit()