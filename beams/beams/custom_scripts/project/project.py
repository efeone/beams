import frappe
from frappe.model.mapper import get_mapped_doc
import json
from frappe import _
from frappe.utils import nowdate

@frappe.whitelist()
def create_adhoc_budget(source_name, target_doc=None):
    """
    Maps fields from the Project doctype to the Adhoc Budget doctype, including the
    selected values from the 'budget_expense_types' field into the child table 'Budget Expense'.
    """
    project_doc = frappe.get_doc('Project', source_name)
    adhoc_budget = get_mapped_doc("Project", source_name, {
        "Project": {
                "doctype": "Adhoc Budget",
                "field_map": {
                    "name": "project",
                    "expected_start_date": "expected_start_date",
                    "expected_end_date": "expected_end_date",
                    "generates_revenue": "generates_revenue"
                }
            }
    }, target_doc)

    for expense_type in project_doc.budget_expense_types:
        adhoc_budget.append('budget_expense', {
            'budget_expense_type': expense_type.budget_expense_type
        })
    return adhoc_budget

@frappe.whitelist()
def create_equipment_hire_request(source_name, target_doc=None):
    """
    Maps fields from the Project doctype to the Equipment Hire Request doctype.
    """
    from frappe.model.mapper import get_mapped_doc

    return get_mapped_doc(
        "Project",
        source_name,
        {
            "Project": {
                "doctype": "Equipment Hire Request",
                "field_map": {
                    "name": "project",
                    "expected_start_date": "required_from",
                    "expected_end_date": "required_to",
                    "bureau": "bureau"
                }
            }
        },
        target_doc
    )


@frappe.whitelist()
def create_transportation_request(source_name, target_doc=None):
    """
    Maps fields from the Project doctype to the Transportation Request doctype'.
    """
    transportation_request = get_mapped_doc("Project", source_name, {
        "Project": {
                "doctype": "Transportation Request",
                "field_map": {
                    "name": "project",
                    "bureau": "bureau"
                }
            }
    }, target_doc)
    return transportation_request

@frappe.whitelist()
def create_technical_support_request(project_id, requirements):
    ''' Create Technical Request document '''

    # Parse the JSON input
    requirements = json.loads(requirements)

    # Validate the Project ID
    if not frappe.db.exists('Project', project_id):
        frappe.throw(_("Invalid Project ID: {0}").format(project_id))

    # Fetch Project details
    project = frappe.get_doc('Project', project_id)

    # Iterate over the requirements and create Technical Requests
    for req in requirements:
        department = frappe.db.get_value("Department", req['department'], "name")
        designation = frappe.db.get_value("Designation", req['designation'], "name")
        bureau =frappe.db.get_value("Project", project_id, "bureau")
        remarks = req.get('remarks', "")
        required_from = req.get('required_from')
        required_to = req.get('required_to')

        # Validate mandatory fields
        if not department or not designation:
            frappe.throw(_("Both Department and Designation are required."))

        # Create the Technical Request document
        doc = frappe.get_doc({
            'doctype': 'Technical Request',
            'project': project_id,
            'department': department,
            'designation': designation,
            'remarks': remarks,
            'posting_date': nowdate(),
            'bureau':bureau,
            'required_from': required_from,
            'required_to': required_to
        })
        doc.insert(ignore_permissions=True)
        frappe.msgprint(_("Technical Request created successfully for project: {0}.").format(project.project_name), indicator="green", alert=1)

    return

@frappe.whitelist()
def get_assigned_resources(cur_project, assigned_from=None, assigned_to=None):
    if not assigned_from and not assigned_to:
        
    project_list = frappe.db.get_all("Project", {"status":"Open", "name":["!=", cur_project]}, pluck="name")
    assigned_employees = list(set(frappe.db.get_all("Allocated Resource Detail", {"parent":["in", project_list], "assigned_to":[">=", assigned_to], "assigned_from":["<=", assigned_from]}, or_filters={"parent":["in", project_list], "assigned_to":["<=", assigned_to], "assigned_from":[">=", assigned_from]}, pluck="employee")))
    return assigned_employees
