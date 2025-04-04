import frappe
from frappe.model.mapper import get_mapped_doc
import json
from frappe import _
from frappe.utils import nowdate
from erpnext.accounts.utils import get_fiscal_year

def validate_project(doc, method):
    for row in doc.get("required_manpower_details"):
        if row.required_from and row.required_to:
            if row.required_from > row.required_to:
                frappe.throw(f"Row {row.idx}: 'Required From' date must be before 'Required To' date.")

def validate_project_dates(doc, method):
    """Validate 'Required From' and 'Required To' dates in the Required Manpower Details child table against the project's Expected Start Date and Expected End Date."""
    if not doc.expected_start_date or not doc.expected_end_date:
        return
    for row in doc.required_manpower_details:
        if row.required_from and row.required_from < doc.expected_start_date:
            frappe.throw(_("Row {0}: Required From ({1}) cannot be before Expected Start Date ({2})").format(
                row.idx, row.required_from, doc.expected_start_date
            ))
        if row.required_to and row.required_to < doc.expected_start_date:
            frappe.throw(_("Row {0}: Required To ({1}) cannot be before Expected Start Date ({2})").format(
                row.idx, row.required_to, doc.expected_start_date
            ))
        if row.required_from and row.required_from > doc.expected_end_date:
            frappe.throw(_("Row {0}: Required From ({1}) cannot be after Expected End Date ({2})").format(
                row.idx, row.required_from, doc.expected_end_date
            ))
        if row.required_to and row.required_to > doc.expected_end_date:
            frappe.throw(_("Row {0}: Required To ({1}) cannot be after Expected End Date ({2})").format(
                row.idx, row.required_to, doc.expected_end_date
            ))

@frappe.whitelist()
def create_adhoc_budget(source_name, target_doc=None):
    '''
    Maps fields from the Project doctype to the Adhoc Budget doctype, including the
    selected values from the 'budget_expense_types' field into the child table 'Budget Expense'.
    '''
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
def map_equipment_acquiral_request(source_name, target_doc=None):
    '''
    Maps fields from the Project doctype to the Equipment Acquiral Request doctype.
    '''
    from frappe.model.mapper import get_mapped_doc

    return get_mapped_doc(
        "Project",
        source_name,
        {
            "Project": {
                "doctype": "Equipment Acquiral Request",
                "field_map": {
                    "name": "project",
                    "expected_start_date": "required_from",
                    "expected_end_date": "required_to",
                    "bureau": "bureau",
                    "location": "location"
                }
            }
        },
        target_doc
    )

@frappe.whitelist()
def map_equipment_request(source_name, target_doc=None):
    '''
    Maps fields from the Project doctype to the Equipment Request doctype.
    '''

    return get_mapped_doc(
        "Project",
        source_name,
        {
            "Project": {
                "doctype": "Equipment Request",
                "field_map": {
                    "name": "project",
                    "expected_start_date": "required_from",
                    "expected_end_date": "required_to",
                    "bureau": "bureau",
                    "location": "location"

                }
            }
        },
        target_doc
    )


@frappe.whitelist()
def create_transportation_request(source_name, target_doc=None):
    transportation_request = get_mapped_doc("Project", source_name, {
        "Project": {
            "doctype": "Transportation Request",
            "field_map": {
                "name": "project",
                "bureau": "bureau",
                "location": "location",
                "expected_start_date": "required_on"
            },
            "field_no_map": ["required_vehicle_details"]
        },
        "Required Vehicle Details": {
            "doctype": "Required Vehicle Details",
            "add_if_empty": True,
            "field_map": {
                "no_of_travellers": "no_of_travellers",
                "from": "from",
                "to": "to",
                "allocated": "allocated",
                "hired": "hired"
            }
        }
    }, target_doc)

    details = frappe.get_all(
        "Required Vehicle Details",
        filters={"parent": source_name, "parenttype": "Project"},
        fields=["from", "to"],
        order_by="idx asc",
        limit=1
    )

    if details:
        setattr(transportation_request, "from", details[0].get("from"))
        setattr(transportation_request, "to", details[0].get("to"))

    if not transportation_request.get("from") or not transportation_request.get("to"):
        frappe.throw("Error: 'From' or 'To' location is missing!")

    transportation_request.save()
    return transportation_request

@frappe.whitelist()
def create_technical_request(project_id):
    '''Create a Technical Request document and map required manpower details from Project.'''

    if not frappe.db.exists('Project', project_id):
        frappe.throw(_("Invalid Project ID: {0}").format(project_id))

    project = frappe.get_doc('Project', project_id)

    doc = frappe.get_doc({
        'doctype': 'Technical Request',
        'project': project_id,
        'posting_date': nowdate(),
        'bureau': project.bureau,
        'location': project.location,
        'required_from': project.expected_start_date,
        'required_to': project.expected_end_date,
        'required_employees': []

    })

    # Fetch manpower details from Project's child table (`required_manpower_details`)
    for man in project.get("required_manpower_details", []):
        department = frappe.db.get_value("Department", man.department, "name")
        designation = frappe.db.get_value("Designation", man.designation, "name")
        no_of_employees = man.get('no_of_employees',1)
        required_from = man.get('required_from')
        required_to = man.get('required_to')

        if not department or not designation:
            frappe.throw(_("Both Department and Designation are required."))

        for _ in range(no_of_employees):
            doc.append("required_employees", {
                "department": department,
                "designation": designation,
                "required_from": man.required_from,
                "required_to": man.required_to,
            })

    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def update_program_request_status_on_project_completion(doc, method):
    """
    Update related Program Request workflow state to 'Closed' when the Project status becomes 'Completed'.
    """
    if doc.status == "Completed":
        # Fetch all related Program Requests linked to this Project
        program_requests = frappe.get_all(
            "Program Request",
            filters={"project": doc.name, "workflow_state": ("!=", "Closed")},
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
    for row in doc.allocated_manpower_details:
        if not row.employee:
            continue
        overlapping_projects = frappe.get_all(
            "Allocated Manpower Detail",
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

@frappe.whitelist()
def get_assets_by_location(location):
    '''Fetch unique item codes of Assets linked to the given Location.'''
    if not location:
        frappe.throw(_("Location is required."))

    assets = frappe.get_all(
        "Asset",
        filters={"location": location},
        pluck="item_code",
        distinct=True
    )

    return assets or []

@frappe.whitelist()
def get_available_quantities(items, location):
    '''
    Get available quantities for specified items at a given location.
    Returns a dictionary with item codes as keys and their available quantities as values.
    '''
    if isinstance(items, str):
        items = json.loads(items)

    if not location:
        frappe.throw(_("Location is required."))

    available_quantities = {item: 0 for item in items}

    # Fetch count of assets matching the given items and location
    for item in items:
        total_quantity = frappe.db.count(
            "Asset",
            filters={
                "item_code": item,
                "location": location
            }
        ) or 0
        available_quantities[item] = total_quantity

    return available_quantities

@frappe.whitelist()
def create_equipment_request(source_name, equipment_data, required_from, required_to):
    '''Creates an Equipment Request for a project with multiple items.'''
    request_data = json.loads(equipment_data)

    if not frappe.db.exists('Project', source_name):
        frappe.throw(_("Invalid Project ID: {0}").format(source_name))

    print("Request Data:", request_data)

    request_doc = frappe.get_doc({
        'doctype': "Equipment Request",
        'project': source_name,
        'required_from': required_from,
        'required_to': required_to,
        'required_equipments': [
            {
                'required_item': data['item'],
                'required_quantity': data['required_quantity'],
                'available_quantity': data['available_quantity']
            }
            for data in request_data
        ]
    })

    request_doc.insert(ignore_permissions=True)
    project_name = frappe.db.get_value('Project', source_name, 'project_name')
    frappe.msgprint(_("Equipment Request created successfully for project: {}.").format(project_name),indicator="green",alert=1)
    return True
