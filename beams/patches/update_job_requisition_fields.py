import frappe

def execute():
    # List of property setters to delete: (DocType, Field Name, Property)
    properties_to_delete = [
        ("Job Requisition", "designation", "mandatory_depends_on"),
        ("Job Requisition", "description", "depends_on"),
        ("Job Requisition", "department", "depends_on"),
        ("Job Requisition", "job_description_template", "mandatory_depends_on"),
        ("Job Requisition", "job_description_template", "depends_on")
    ]

    # Delete existing property setters
    for doctype, field_name, property in properties_to_delete:
        filters = {
            "doctype_or_field": "DocField",
            "doc_type": doctype,
            "field_name": field_name,
            "property": property
        }
        if frappe.db.exists("Property Setter", filters):
            frappe.db.delete("Property Setter", filters)

    # Create new property setters
    new_properties = [
        {
            "field": "description",
            "property": "depends_on",
            "value": "eval: !['Draft', 'Pending HOD Verification'].includes(doc.workflow_state)"
        },
        {
            "field": "department",
            "property": "depends_on",
            "value": "eval:doc.request_for=='Employee Replacement'"
        },
        {
            "field": "job_description_template",
            "property": "depends_on",
            "value": "eval: frappe.user_roles.includes('HR Manager') && doc.workflow_state == 'Pending HR Approval'"
        }
    ]

    for prop in new_properties:
        frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": "Job Requisition",
            "field_name": prop["field"],
            "property": prop["property"],
            "value": prop["value"],
            "property_type": "Data"
        }).insert(ignore_if_duplicate=True)

    frappe.db.commit()