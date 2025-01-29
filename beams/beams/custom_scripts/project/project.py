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
def map_equipment_hire_request(source_name, target_doc=None):
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
def map_equipment_request(source_name, target_doc=None):
    """
    Maps fields from the Project doctype to the Equipment Request doctype.
    """

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
def get_available_quantities(items, bureau):
    """
    Get available quantities for items at locations matching the bureau.
    Returns a dictionary with item codes as keys and their available quantities as values.
    """
    if isinstance(items, str):
        items = json.loads(items)

    available_quantities = {}

    # Get the location for the given bureau (assuming location name matches bureau name)
    location = bureau  # Since location and bureau names are same

    if location:
        for item in items:
            # Count assets matching item_code, bureau and location
            total_quantity = frappe.db.count(
                "Asset",
                filters={
                    "item_code": item,
                    "bureau": bureau,
                    "location": location
                }
            ) or 0
            available_quantities[item] = total_quantity

    else:
        available_quantities = {item: 0 for item in items}

    return available_quantities

@frappe.whitelist()
def create_equipment_request(source_name, equipment_data):
    """Creates an Equipment Request for a project with multiple items."""
    equipment_data = json.loads(equipment_data)

    if not frappe.db.exists('Project', source_name):
        frappe.throw(_("Invalid Project ID: {0}").format(source_name))

    request_doc = frappe.get_doc({
        'doctype': "Equipment Request",
        'project': source_name,
        'required_equipments': [
            {
                'item': data['item'],
                'quantity': data['quantity'],
                'required_from': data.get('required_from'),
                'required_to': data.get('required_to')
            }
            for data in equipment_data
        ]
    })

    request_doc.insert(ignore_permissions=True)

    project_name = frappe.db.get_value('Project', source_name, 'project_name')
    frappe.msgprint(
        _("Equipment Request created successfully for project: {}.").format(project_name),
        indicator="green",
        alert=1
    )

    return True

@frappe.whitelist()
def create_equipment_hire_request(source_name, equipment_data):
    """Creates an Equipment Hire Request for a project with multiple items."""
    equipment_data = json.loads(equipment_data)

    if not frappe.db.exists('Project', source_name):
        frappe.throw(_("Invalid Project ID: {0}").format(source_name))

    hire_doc = frappe.get_doc({
        'doctype': "Equipment Hire Request",
        'project': source_name,
        'required_items': [
            {
                'item': data['item'],
                'quantity': data['required_quantity'],
                'required_from': data.get('required_from'),
                'required_to': data.get('required_to')
            }
            for data in equipment_data
        ]
    })

    hire_doc.insert(ignore_permissions=True)

    project_name = frappe.db.get_value('Project', source_name, 'project_name')
    frappe.msgprint(
        _("Equipment Hire Request created successfully for project: {}.").format(project_name),
        indicator="green",
        alert=1
    )

    return True

@frappe.whitelist()
def get_assets_by_bureau(bureau):
    """Fetch item codes of Assets linked to the given Bureau."""
    if not bureau:
        return []

    return frappe.get_all(
        "Asset",
        filters={"bureau": bureau},
        pluck="item_code",
        distinct=True
    ) or []
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
