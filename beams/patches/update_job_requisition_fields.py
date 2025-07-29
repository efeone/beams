import frappe

def execute():
    # Remove mandatory_depends_on for 'designation'
    designation_filter = {
        "doctype_or_field": "DocField",
        "doc_type": "Job Requisition",
        "field_name": "designation",
        "property": "mandatory_depends_on",
    }
    designation_ps = frappe.db.exists("Property Setter", designation_filter)
    if designation_ps:
        frappe.db.delete("Property Setter", {"name": designation_ps})

    # Update depends_on for 'description'
    frappe.get_doc({
        "doctype": "Property Setter",
        "doctype_or_field": "DocField",
        "doc_type": "Job Requisition",
        "field_name": "description",
        "property": "depends_on",
        "value": "eval: !['Draft', 'Pending HOD Verification'].includes(doc.workflow_state)",
        "property_type": "Data"
    }).insert(ignore_if_duplicate=True)

    # Add depends_on for 'department'
    frappe.get_doc({
        "doctype": "Property Setter",
        "doctype_or_field": "DocField",
        "doc_type": "Job Requisition",
        "field_name": "department",
        "property": "depends_on",
        "value": "eval:doc.request_for=='Employee Replacement'",
        "property_type": "Data"
    }).insert(ignore_if_duplicate=True)

    # Replace mandatory_depends_on with depends_on for 'job_description_template'
    jdt_filter = {
        "doctype_or_field": "DocField",
        "doc_type": "Job Requisition",
        "field_name": "job_description_template",
        "property": "mandatory_depends_on",
    }
    jdt_ps = frappe.db.exists("Property Setter", jdt_filter)
    if jdt_ps:
        frappe.db.delete("Property Setter", {"name": jdt_ps})

    frappe.get_doc({
        "doctype": "Property Setter",
        "doctype_or_field": "DocField",
        "doc_type": "Job Requisition",
        "field_name": "job_description_template",
        "property": "depends_on",
        "value": "eval: frappe.user_roles.includes('HR Manager') && doc.workflow_state == 'Pending HR Approval'",
        "property_type": "Data"
    }).insert(ignore_if_duplicate=True)

    frappe.db.commit()
