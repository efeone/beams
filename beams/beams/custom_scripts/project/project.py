import json
import frappe
from erpnext.accounts.utils import get_fiscal_year
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import nowdate
from frappe.utils import now
from frappe.utils import cint, now


def validate_project(doc, method):
    for row in doc.get("required_manpower_details"):
        if row.required_from and row.required_to:
            if row.required_from > row.required_to:
                frappe.throw(f"Row {row.idx}: 'Required From' date must be before 'Required To' date.")

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

    '''Create  Transportation Request document and map required vehicle details from Project.'''

    all_rvds = frappe.get_all(
        "Required Vehicle Details",
        filters={"parent": source_name, "parenttype": "Project"},
        fields=["name", "from", "to", "no_of_travellers", "required_vehicle_details"],
        order_by="idx asc"
    )

    allocated_vehicles = frappe.get_all(
        "Allocated Vehicle Details",
        filters={"parent": source_name, "parenttype": "Project"},
        fields=["from", "to", "no_of_travellers", "status"]
    )

    allocated_route_counts = {}
    for allocated in allocated_vehicles:
        if allocated.get("status") in ["Allocated", "Hired"]:
            route_key = (allocated.get("from"), allocated.get("to"))
            if route_key in allocated_route_counts:
                allocated_route_counts[route_key] += 1
            else:
                allocated_route_counts[route_key] = 1

    total_route_counts = {}
    for rvd in all_rvds:
        route_key = (rvd.get("from"), rvd.get("to"))
        if route_key in total_route_counts:
            total_route_counts[route_key] += 1
        else:
            total_route_counts[route_key] = 1

    unallocated_rvds = []
    processed_routes = {}

    for rvd in all_rvds:
        route_key = (rvd.get("from"), rvd.get("to"))
        allocated_count = allocated_route_counts.get(route_key, 0)

        processed_count = processed_routes.get(route_key, 0)

        if processed_count < (total_route_counts.get(route_key, 0) - allocated_count):
            unallocated_rvds.append(rvd)
            processed_routes[route_key] = processed_count + 1

    if not unallocated_rvds:
        frappe.throw("All Required Vehicle Details have already been allocated or hired. Cannot create Transportation Request.")

    # Create the Transportation Request document
    transportation_request = frappe.new_doc("Transportation Request")

    project = frappe.get_doc("Project", source_name)

    transportation_request.project = source_name
    transportation_request.bureau = project.bureau
    transportation_request.location = project.location
    transportation_request.required_on = project.expected_start_date
    transportation_request.requirements = "Transportation for project " + source_name

    setattr(transportation_request, "from", unallocated_rvds[0].get("from"))
    setattr(transportation_request, "to", unallocated_rvds[0].get("to"))

    if not transportation_request.get("from") or not transportation_request.get("to"):
        frappe.throw("Error: 'From' or 'To' location is missing!")

    for rvd in unallocated_rvds:
        row = transportation_request.append("required_vehicle", {})
        row.no_of_travellers = rvd.no_of_travellers
        setattr(row, "from", rvd.get("from"))
        setattr(row, "to", rvd.get("to"))
        row.allocated = rvd.allocated
        row.hired = rvd.hired
        row.required_vehicle_details = rvd.required_vehicle_details

    transportation_request.save()
    return transportation_request

@frappe.whitelist()
def validate_vehicle_assignment_in_same_project(doc, method):
    '''
    Validate that a vehicle is not assigned to multiple times in the same project during the same time period.
    '''
    vehicle_assignments = {}

    for row in doc.allocated_vehicle_details:
        if not row.vehicle:
            continue

        from_date = getattr(row, 'from', None)
        to_date = getattr(row, 'to', None)

        if not from_date or not to_date:
            continue

        if row.vehicle not in vehicle_assignments:
            vehicle_assignments[row.vehicle] = []

        for existing_row in vehicle_assignments[row.vehicle]:
            existing_from = getattr(existing_row, 'from', None)
            existing_to = getattr(existing_row, 'to', None)

            if existing_from and existing_to:
                if (
                    (existing_from <= to_date) and
                    (existing_to >= from_date)
                ):
                    frappe.throw(f"Vehicle {row.vehicle} is already assigned for this same project ({doc.name}) during the same time period.")

        vehicle_assignments[row.vehicle].append(row)


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

    any_valid_row = False

    for req_row in project.required_manpower_details:
        if not req_row.department or not req_row.designation or not req_row.no_of_employees:
            continue

        department = req_row.department
        designation = req_row.designation
        required_no_of_employees = req_row.no_of_employees
        required_from = req_row.required_from
        required_to = req_row.required_to

        assigned_employees = frappe.get_all(
            "Allocated Manpower Detail",
            filters={
                "parent": project.name,
                "department": department,
                "designation": designation,
                "assigned_from": ["<=", required_to],
                "assigned_to": [">=", required_from]
            },
            fields=["employee"]
        )

        unique_assigned_employees = set(row.employee for row in assigned_employees)
        assigned_count = len(unique_assigned_employees)

        if assigned_count > required_no_of_employees:
            frappe.throw(_(
                "Cannot create a Technical Request. The number of employees assigned to the department '{0}' and designation '{1}' exceeds the required number ({2}) during the period {3} to {4}. "
                "Currently assigned: {5} employees in project {6}."
            ).format(
                department, designation, required_no_of_employees, required_from, required_to, assigned_count, project.name
            ))

        elif assigned_count == required_no_of_employees:
            frappe.msgprint(_(
                "Note: The number of employees assigned to department '{0}' and designation '{1}' has already reached the required number ({2}) for the period {3} to {4}."
            ).format(
                department, designation, required_no_of_employees, required_from, required_to
            ))
            continue

        remaining_needed = required_no_of_employees - assigned_count
        any_valid_row = True

        for i in range(remaining_needed):
            doc.append("required_employees", {
                "department": department,
                "designation": designation,
                "required_from": required_from,
                "required_to": required_to,
            })

    if not any_valid_row:
        frappe.throw(_("No new manpower requirements available for assignment. All requirements are already fulfilled."))

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
                "assigned_to": [">=", row.assigned_from],
                "parenttype": "Technical Request",
                "parentfield": "allocated_manpower_details",
            },
            pluck="parent"
        )
        if overlapping_projects:
            employee_name = frappe.get_value("Employee", row.employee, "employee_name")
            frappe.throw(f"Employee {employee_name} ({row.employee}) is already assigned to another project ({', '.join(overlapping_projects)}) within the same time period.")

@frappe.whitelist()
def validate_employee_assignment_in_same_project(doc, method):
    '''
    Validate that an employee is not assigned to multiple roles/tasks within the same project during the same time period.
    '''
    employee_assignments = {}

    for row in doc.allocated_manpower_details:
        if not row.employee:
            continue

        if row.employee not in employee_assignments:
            employee_assignments[row.employee] = []

        for existing_row in employee_assignments[row.employee]:
            if (
                (existing_row.assigned_from <= row.assigned_to) and
                (existing_row.assigned_to >= row.assigned_from)
            ):
                employee_name = frappe.get_value("Employee", row.employee, "employee_name")
                frappe.throw(f"Employee {employee_name} ({row.employee}) is already assigned to another task or role within the same project ({doc.name}) during the same time period.")

        employee_assignments[row.employee].append(row)


@frappe.whitelist()
def create_equipment_request(source_name, equipment_data, required_from, required_to):
    """Creates an Equipment Request for a project with multiple items."""

    try:
        request_data = json.loads(equipment_data)
    except Exception as e:
        frappe.throw(_("Invalid equipment data format. Error: {}").format(str(e)))

    if not frappe.db.exists('Project', source_name):
        frappe.throw(_("Invalid Project ID: {0}").format(source_name))

    if not request_data:
        frappe.throw(_("No equipment data found to create request."))

    # Create the Equipment Request doc
    request_doc = frappe.new_doc("Equipment Request")
    request_doc.project = source_name
    request_doc.required_from = required_from
    request_doc.required_to = required_to

    for item in request_data:
        request_doc.append('required_equipments', {
            'required_item': item.get('item'),
            'required_quantity': item.get('required_quantity'),
            'available_quantity': item.get('available_quantity', 0)
        })

    # Save and commit the doc
    request_doc.insert(ignore_permissions=True)

    # Show success message with document link
    frappe.msgprint(
        msg=_("Equipment Request <a href='/app/equipment-request/{0}'>{0}</a> created successfully for project.".format(request_doc.name)),
        title=_("Success"),
        indicator='green',
        alert=True
    )

    return request_doc.name


@frappe.whitelist()
def get_available_quantities(items, source_name=None):
    """Returns available quantities for specified items based on location from Project or Beams Admin Settings."""

    if isinstance(items, str):
        items = json.loads(items)

    if not isinstance(items, list):
        frappe.throw("Items should be a list.")

    location = None

    if source_name:
        location = frappe.db.get_value("Project", source_name, "asset_location")

    if not location:
        location = frappe.db.get_single_value("Beams Admin Settings", "default_asset_location")

    if not location:
        frappe.msgprint("Asset location not configured in Project or Beams Admin Settings.")
        return {"_error": "Asset location not configured in Project or Beams Admin Settings."}


    result = {}
    for item in items:
        if item:
            quantity = frappe.db.count("Asset", {
                "item_code": item,
                "location": location,
                "docstatus": 1
            })
            result[item] = quantity or 0

    return result

def sync_manpower_logs(doc, method):
    """
    Sync manpower logs from Project without removing return-related data.
    """
    source_child_table = "allocated_manpower_details"
    target_child_table = "allocated_manpower_detail"

    log_name = frappe.db.get_value("Manpower Transaction Log", {"project": doc.name})

    if log_name:
        transaction_log = frappe.get_doc("Manpower Transaction Log", log_name)
    else:
        transaction_log = frappe.new_doc("Manpower Transaction Log")
        transaction_log.project = doc.name
        transaction_log.project_name = doc.project_name

    if not transaction_log.meta.get_field(target_child_table):
        frappe.throw(f"Child table field '{target_child_table}' not found in Manpower Transaction Log")

    existing_logs = {
        (row.employee, row.hired_personnel, str(row.assigned_from), str(row.assigned_to)): row
        for row in transaction_log.get(target_child_table)
    }

    updated_rows = []

    for row in doc.get(source_child_table) or []:
        key = (row.employee, row.hired_personnel, str(row.assigned_from), str(row.assigned_to))
        existing = existing_logs.get(key)

        if existing:
            updated_rows.append({
                "department": row.department,
                "designation": row.designation,
                "assigned_from": row.assigned_from,
                "assigned_to": row.assigned_to,
                "employee": row.employee,
                "hired_personnel": row.hired_personnel,
                "hired_personnel_contact_info": row.hired_personnel_contact_info,
                "status": row.status,
                "returned": existing.returned,
                "returned_date": existing.returned_date,
                "returned_reason": existing.returned_reason
            })
        else:
            updated_rows.append({
                "department": row.department,
                "designation": row.designation,
                "assigned_from": row.assigned_from,
                "assigned_to": row.assigned_to,
                "employee": row.employee,
                "hired_personnel": row.hired_personnel,
                "hired_personnel_contact_info": row.hired_personnel_contact_info,
                "status": row.status
            })

    transaction_log.set(target_child_table, [])
    for data in updated_rows:
        transaction_log.append(target_child_table, data)
    transaction_log.save(ignore_permissions=True)


@frappe.whitelist()
def update_return_details_in_log(project, assigned_from, returned_date, returned_reason, employee=None, hired_personnel=None):
    log_name = frappe.db.get_value("Manpower Transaction Log", {"project": project})
    if not log_name:
        frappe.throw(_("No Manpower Transaction Log found for this project."))

    log_doc = frappe.get_doc("Manpower Transaction Log", log_name)
    updated = False

    for row in log_doc.allocated_manpower_detail:
        match_employee = employee and row.employee == employee
        match_hired = hired_personnel and row.hired_personnel == hired_personnel
        match_assigned = str(row.assigned_from) == str(assigned_from)

        if match_assigned and (match_employee or match_hired):
            row.returned = 1
            row.returned_date = returned_date
            row.returned_reason = returned_reason
            updated = True
            break

    if updated:
        log_doc.save(ignore_permissions=True)
    else:
        frappe.throw(_("No matching manpower record found in the transaction log."))


def on_update_project(doc, method):
    """Mark manpower records as returned when a project is Completed."""

    if doc.workflow_state != "Completed":
        return

    log_name = frappe.db.get_value("Manpower Transaction Log", {"project": doc.name})
    if not log_name:
        return

    log_doc = frappe.get_doc("Manpower Transaction Log", log_name)

    updated = False
    for row in log_doc.allocated_manpower_detail:
        if not row.returned:
            row.returned = 1
            row.returned_date = now()
            row.returned_reason = "Project Completed"
            updated = True

    if updated:
        log_doc.save(ignore_permissions=True)
        frappe.msgprint(f"Manpower records marked as returned for Project {doc.name}")

def sync_vehicle_logs(doc, method):
    """
    Sync vehicle transaction logs from Project's allocated_vehicle_details to
    Vehicle Transaction Log's vehicle_log_details, while preserving return data.
    """

    source_child_table = "allocated_vehicle_details"
    target_child_table = "vehicle_log_details"

    log_name = frappe.db.get_value("Vehicle Transaction Log", {"project": doc.name})

    if log_name:
        transaction_log = frappe.get_doc("Vehicle Transaction Log", log_name)
    else:
        transaction_log = frappe.new_doc("Vehicle Transaction Log")
        transaction_log.project = doc.name
        transaction_log.project_name = doc.project_name

    if not transaction_log.meta.get_field(target_child_table):
        frappe.throw(f"Child table field '{target_child_table}' not found in Vehicle Transaction Log")

    existing_logs = {
        row.vehicle: row
        for row in transaction_log.get(target_child_table)
    }

    updated_rows = []

    for row in doc.get(source_child_table) or []:
        vehicle = row.vehicle
        existing = existing_logs.get(vehicle)

        from_location = frappe.db.get_value("Location", row.get("from"), "location_name") or row.get("from")
        to_location = frappe.db.get_value("Location", row.get("to"), "location_name") or row.get("to")

        log_data = {
            "vehicle": vehicle,
            "from": from_location,
            "to": to_location,
            "no_of_travellers": row.no_of_travellers,
            "status": row.status,
        }

        if existing:
            log_data["return_date"] = existing.return_date
            log_data["return_reason"] = existing.return_reason

        updated_rows.append(log_data)

    transaction_log.set(target_child_table, [])
    for data in updated_rows:
        transaction_log.append(target_child_table, data)

    transaction_log.save(ignore_permissions=True)

@frappe.whitelist()
def update_vehicle_return_details_in_log(project, vehicle, return_date, return_reason):
    """
    Updates the return details of a vehicle in the 'Vehicle Transaction Log' for the given project.
    """
    log_name = frappe.db.get_value("Vehicle Transaction Log", {"project": project})
    if not log_name:
        frappe.throw(_("No Vehicle Transaction Log found for this project."))

    log_doc = frappe.get_doc("Vehicle Transaction Log", log_name)
    updated = False

    for row in log_doc.vehicle_log_details:
        if row.vehicle == vehicle and not row.returned:
            row.returned = True
            row.return_date = return_date
            row.return_reason = return_reason
            updated = True
    if updated:
        log_doc.save(ignore_permissions=True)
    else:
        frappe.throw(_("No matching vehicle record found in the transaction log."))

def auto_return_vehicles_on_project_completion(doc, method):
    """
    Automatically marks vehicles as returned in the 'Vehicle Transaction Log'
    when the associated project is marked as 'Completed' or 'Cancelled'.
    """
    if doc.status not in ("Completed", "Cancelled"):
        return

    log_name = frappe.db.get_value("Vehicle Transaction Log", {"project": doc.name})
    if not log_name:
        return

    log_doc = frappe.get_doc("Vehicle Transaction Log", log_name)
    updated = False

    for row in log_doc.vehicle_log_details:
        if not row.returned and not row.return_date and not row.return_reason:
            row.returned = True
            row.return_date = frappe.utils.nowdate()
            row.return_reason = "Project Completed" if doc.status == "Completed" else "Project Cancelled"
            updated = True

        elif row.return_reason and row.return_date:
            row.returned = True
            updated = True

        else:
            print(f" - Skipped (already returned or reason provided)")

    if updated:
        log_doc.save(ignore_permissions=True)



def sync_equipment_logs(doc, method):
    """
    Sync equipment transaction logs from Project without removing return-related data.
    """
    source_child_table = "allocated_item_details"
    target_child_table = "item_log_details"

    log_name = frappe.db.get_value("Equipment Transaction Log", {"project": doc.name})

    if log_name:
        transaction_log = frappe.get_doc("Equipment Transaction Log", log_name)
    else:
        transaction_log = frappe.new_doc("Equipment Transaction Log")
        transaction_log.project = doc.name
        transaction_log.insert(ignore_permissions=True)

    if not transaction_log.meta.get_field(target_child_table):
        frappe.throw(f"Child table field '{target_child_table}' not found in Equipment Transaction Log")

    existing_logs = {
        row.required_item: row for row in transaction_log.get(target_child_table)
    }

    updated_rows = []

    for row in doc.get(source_child_table) or []:
        existing = existing_logs.get(row.required_item)

        updated_rows.append({
            "required_item": row.required_item,
            "available_quantity": row.available_quantity,
            "required_quantity": row.required_quantity,
            "issued_quantity": row.issued_quantity,
            "acquired_quantity": row.acquired_quantity,
            "returned_count": existing.returned_count if existing else "0",
            "returned_reason": existing.returned_reason if existing else "",
            "return_date": existing.return_date if existing else None
        })

    transaction_log.set(target_child_table, [])
    for data in updated_rows:
        transaction_log.append(target_child_table, data)

    transaction_log.save(ignore_permissions=True)


@frappe.whitelist()
def update_return_details_in_equipment_log(project, required_item, return_date, returned_reason, returned_count):
    """
    Update return details in the Equipment Transaction Log for a specific equipment item.
    """
    log_name = frappe.db.get_value("Equipment Transaction Log", {"project": project})
    if not log_name:
        frappe.throw(_("No Equipment Transaction Log found for this project."))

    log_doc = frappe.get_doc("Equipment Transaction Log", log_name)
    updated = False

    for row in log_doc.item_log_details:
        if row.required_item == required_item:
            row.return_date = return_date
            existing_reason = row.returned_reason or ""
            new_reason_entry = f"{returned_reason} | Returned On: {return_date} | Returned Count: {returned_count}"
            row.returned_reason = existing_reason + ("\n" if existing_reason else "") + new_reason_entry
            row.returned_count = (row.returned_count or 0) + int(returned_count)
            updated = True
            break

    if updated:
        log_doc.save(ignore_permissions=True)
    else:
        frappe.throw(_("No matching equipment record found in the transaction log."))

def auto_return_equipment_on_project_completion(doc, method):
    if doc.status not in ["Completed", "Cancelled"]:
        return

    log_name = frappe.db.get_value("Equipment Transaction Log", {"project": doc.name})
    if not log_name:
        return

    log_doc = frappe.get_doc("Equipment Transaction Log", log_name)
    updated = False

    for row in log_doc.item_log_details:
        total_issued = cint(row.issued_quantity) + cint(row.acquired_quantity)
        pending_return = total_issued - cint(row.returned_count)

        if pending_return > 0:
            row.return_date = now()
            row.returned_reason = (row.returned_reason or "") + f"\nProject {doc.status} | Returned Count: {pending_return}"
            row.returned_count = total_issued
            updated = True

    if updated:
        log_doc.save(ignore_permissions=True)
        frappe.msgprint(f"Unreturned Item records marked as returned due to project {doc.status.lower()}.")
