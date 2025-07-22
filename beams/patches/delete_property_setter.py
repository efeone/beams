import frappe

def execute():
    # Define the filter to find the Property Setter
    filters = {
        "doctype_or_field": "DocField",
        "doc_type": "Employee Feedback Rating",
        "field_name": "Rating",
        "property": "read_only",
        "property_type": "Check",
        "value": "1"  
    }

    # Find and delete the property setter if it exists
    property_setter_name = frappe.db.exists("Property Setter", filters)
    if property_setter_name:
        frappe.db.delete("Property Setter", {"name": property_setter_name})
        frappe.db.commit()
