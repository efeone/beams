import frappe
from frappe.model.mapper import get_mapped_doc
import json
from frappe import _
from frappe.utils import nowdate
from erpnext.accounts.utils import get_fiscal_year

@frappe.whitelist()
def create_adhoc_budget(source_name, target_doc=None):
    """
    Maps fields from the Project doctype to the Adhoc Budget doctype, including the
    selected values from the 'budget_expense_types' field into the child table 'Budget Expense'.
    """
    project_doc = frappe.get_doc('Project', source_name)
    fiscal_year = get_fiscal_year()["name"]
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
    if fiscal_year:
        adhoc_budget.fiscal_year = fiscal_year
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
def create_equipment_request(source_name, target_doc=None):
    """
    Maps fields from the Equipment Request doctype to the Project doctype'.
    """
    equipment_request = get_mapped_doc("Project", source_name, {
        "Project": {
                "doctype": "Equipment Request",
                "field_map": {
                    "name": "project",
                    "bureau": "bureau"
                }
            }
    }, target_doc)
    return equipment_request

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
def update_program_request_status_on_project_completion(doc, method):
    """
    Update related Program Request workflow state to 'Closed' when the Project status becomes 'Completed'.
    """
    if doc.status == "Completed":
        # Fetch all related Program Requests linked to this Project
        program_requests = frappe.get_all(
            "Program Request",
            filters={"project": doc.name, "workflow_state": ("!=", "Closed")},  # Exclude already "Closed" state
            fields=["name"]
        )

        # Update the workflow state of each Program Request to 'Closed'
        for request in program_requests:
            program_request = frappe.get_doc("Program Request", request["name"])

            # Update the workflow state to 'Closed' if not already in 'Closed'
            if program_request.workflow_state != "Closed":
                program_request.workflow_state = "Closed"
                program_request.save()  # Save the document

@frappe.whitelist()
def validate_employee_assignment(doc, method):
    """
    Validate that an employee is not assigned to multiple projects during the same time period.
    """
    for row in doc.allocated_resources_details:
        if not row.employee:
            continue
        overlapping_projects = frappe.get_all(
            "Allocated Resource Detail",
            filters={
                "employee": row.employee,
                "parent": ["!=", doc.name],
                "assigned_from": ["<=", row.assigned_to],
                "assigned_to": [">=", row.assigned_from]
            },
            pluck="parent"
        )
        if overlapping_projects:
            employee_name = frappe.get_value("Employee", row.employee, "employee_name")
            frappe.throw(f"Employee {employee_name} ({row.employee}) is already assigned to another project ({', '.join(overlapping_projects)}) within the same time period.")
