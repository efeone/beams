import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import  get_url_to_form
from frappe.model.document import Document

@frappe.whitelist()
# Create a Company Policy Acceptance Log  Document by mapping fields from employee onboarding
def create_cpal(source_name):
    # Get the Employee Onboarding document
    onboarding_doc = frappe.get_doc('Employee Onboarding', source_name)

    # Check if a CPAL already exists for this Employee Onboarding document
    existing_cpal = frappe.db.get_value('Company Policy Acceptance Log',
                                        {'employee': onboarding_doc.employee, 'company': onboarding_doc.company},
                                        'name')

    if existing_cpal:
        # If a CPAL already exists, return the existing CPAL document name
        return existing_cpal

    # Fetch the company_policy from the Company doctype
    company_policy = frappe.db.get_value('Company', onboarding_doc.company, 'company_policy')

    # Create a mapped document using get_mapped_doc
    cpal_doc = get_mapped_doc(
        "Employee Onboarding",
        source_name,
        {
            "Employee Onboarding": {
                "doctype": "Company Policy Acceptance Log",
                "field_map": {
                    "employee": "employee",
                    "employee_name": "employee_name",
                    "department": "department",
                    "date_of_joining": "date_of_joining",
                    "company": "company"
                }
            }
        }
    )
    cpal_doc.insert(ignore_permissions=True)
    return cpal_doc.name

@frappe.whitelist()
def get_employee_details(employee_id):
        employee = frappe.get_doc('Employee', employee_id)
        return {
            'department': employee.department,
            'designation': employee.designation,
            'date_of_joining': employee.date_of_joining,
            'holiday_list': employee.holiday_list,
            'employee_grade': employee.grade
        }

@frappe.whitelist()
def get_excluded_job_applicants():
    # Get job applicants linked to active employees
    job_applicants_with_active_employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "job_applicant": ["!=", ""]},
        pluck="job_applicant"
    )

    # Get job applicants linked to Employee Onboarding (excluding canceled)
    job_applicants_with_onboarding = frappe.get_all(
        "Employee Onboarding",
        filters={"docstatus": ["!=", 2]},
        pluck="job_applicant"
    )

    # Get applicants who satisfy **both** conditions
    excluded_applicants = list(set(job_applicants_with_active_employees) & set(job_applicants_with_onboarding))

    return excluded_applicants if excluded_applicants else []


@frappe.whitelist()
def after_submit(doc_name):
    """
    Triggers Asset Transfer Requests only once after submission if the 'employee' field has a value.
    Prevents duplicate requests by checking existing records.
    """
    doc = frappe.get_doc("Employee Onboarding", doc_name)
    if not doc.employee:
        return
    existing_request = frappe.db.exists("Asset Transfer Request", {"employee": doc.employee})
    if not existing_request:
        create_asset_transfer_requests(doc)

@frappe.whitelist()
def create_asset_transfer_requests(doc, *args, **kwargs):
    doc = frappe.parse_json(doc) if isinstance(doc, str) else doc
    source_doc = frappe.get_doc("Employee Onboarding", doc.name)
    if not source_doc.employee:
        return
    employee = source_doc.employee
    employee_doc = frappe.get_doc("Employee", employee)
    bureau = employee_doc.bureau
    if not bureau:
        frappe.throw("The 'Bureau' field is required in the Employee", title="Missing Bureau")
    bureau_doc = frappe.get_doc("Bureau", bureau)
    location = bureau_doc.location
    if not location:
        frappe.throw("The 'Location' field is required in the Bureau", title="Missing Location")
    assigned_assets = [row.get("asset") for row in source_doc.get("assigned_assets", []) if row.get("asset")]
    assigned_bundles = [row.get("asset_bundle") for row in source_doc.get("assigned_bundles", []) if row.get("asset_bundle")]
    if not assigned_assets and not assigned_bundles:
        return
    asset_transfer_requests = []
    for asset_name in assigned_assets:
        asset_name = asset_name.strip()
        if asset_name:
            asset_transfer_request = frappe.get_doc({
                "doctype": "Asset Transfer Request",
                "asset_type": "Single Asset",
                "asset": asset_name,
                "employee": employee,
                "location": location
            })
            asset_transfer_request.insert()
            asset_transfer_requests.append(asset_transfer_request)
    for bundle_name in assigned_bundles:
        bundle_name = bundle_name.strip()
        if bundle_name:
            asset_transfer_request = frappe.get_doc({
                "doctype": "Asset Transfer Request",
                "asset_type": "Bundle",
                "bundle": bundle_name,
                "employee": employee,
                "location": location
            })
            asset_transfer_request.insert()
            asset_transfer_requests.append(asset_transfer_request)
    if asset_transfer_requests:
        links = "<br>".join(
            f'<a href="{frappe.utils.get_url_to_form(req.doctype, req.name)}">{req.name}</a>'
            for req in asset_transfer_requests
        )
        frappe.msgprint(f'Asset Transfer Requests Created:<br>{links}', alert=True, indicator='green')
