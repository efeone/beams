# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url_to_form, today


class EmployeeTravelRequest(Document):
    def on_cancel(self):
        # Validate that "Reason for Rejection" is provided if the status is "Rejected"
        if self.workflow_state == "Rejected" and not self.reason_for_rejection:
            frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

    def validate(self):
        self.validate_dates()
        self.validate_expected_time()
        self.total_days_calculate()

    def before_save(self):
        self.validate_posting_date()
        if not self.requested_by:
            return

        # Fetch the Batta Policy for the employee
        batta_policy = get_batta_policy(self.requested_by)
        if batta_policy:
            self.batta_policy = batta_policy.get("name")

    @frappe.whitelist()
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                frappe.throw("End Date cannot be earlier than Start Date.")
                if self.start_date < today():
                    frappe.throw("Start Date cannot be in the past.")

    def on_update_after_submit(self):
        if self.workflow_state == "Approved":
            self.create_missing_trip_sheets_for_etr()

        # Trigger only when state becomes Approved
        if self.workflow_state != "Approved":
            return

        # Validation: Rejection reason must be empty when approved
        if self.reason_for_rejection:
            frappe.throw(title="Approval Error", msg="You cannot approve this request if 'Reason for Rejection' is filled.")

        if self.is_vehicle_required:
            if not self.travel_vehicle_allocation:
                frappe.throw(title="Approval Error", msg="Vehicle allocation is required before final approval.")

            has_complete_allocation = False
            for allocation in self.travel_vehicle_allocation:
                if allocation.vehicle and allocation.driver:
                    has_complete_allocation = True
                    break

            if not has_complete_allocation:
                frappe.throw(title="Approval Error",
                            msg="You must allocate driver and vehicle before final approval.")


        if not self.mark_attendance:
            return

        employees = []

        # Add main employee
        if self.requested_by:
            employees.append(self.requested_by)

        # Add employees from child table
        for row in self.travellers:
            if row.employee:
                employees.append(row.employee)

        # Remove duplicates and empty entries
        employees = list(set(filter(None, employees)))

        for emp in employees:
            overlapping = frappe.db.exists(
                "Attendance Request",
                {
                    "employee": emp,
                    "from_date": ["<=", self.end_date],
                    "to_date": [">=", self.start_date],
                    "docstatus": ["!=", 2]
                }
            )

            if overlapping:
                continue

            attendance = frappe.get_doc({
                "doctype": "Attendance Request",
                "employee": emp,
                "from_date": self.start_date,
                "to_date": self.end_date,
                "request_type": "On Duty",
                "company": frappe.db.get_value("Employee", emp, "company"),
                "description": f"From Travel Request {self.name}",
                "reason": "On Duty"
            })

            attendance.insert(ignore_permissions=True)
            frappe.msgprint(f"Attendance Request created for {emp}", alert=True, indicator='green')

    def create_missing_trip_sheets_for_etr(doc):
        '''
        Create Trip Sheets for vehicles in the Travel Vehicle Allocation child table
        if no Trip Sheet exists yet for the current Employee Travel Request (ETR).
        '''
        etr_name = doc.name
        linked_ts_rows = frappe.get_all(
            "Employee Travel Request Details",
            filters={"employee_travel_request": etr_name},
            fields=["parent"]
        )
        ts_names = [row.parent for row in linked_ts_rows]

        existing_ts = frappe.get_all(
            "Trip Sheet",
            filters={"name": ["in", ts_names], "docstatus": ["!=", 2]},
            fields=["name", "vehicle"]
        )

        existing_vehicles_with_ts = {ts.vehicle for ts in existing_ts}

        allocations = [{
            "vehicle": row.vehicle,
            "driver": row.driver
        } for row in doc.travel_vehicle_allocation]

        if not existing_ts:
            vehicles_to_create = allocations
        else:
            vehicles_to_create = [alloc for alloc in allocations if alloc["vehicle"] not in existing_vehicles_with_ts]

        for alloc in vehicles_to_create:
            vehicle = alloc["vehicle"]
            driver = alloc.get("driver")
            safety_inspection = frappe.get_all(
                "Vehicle Safety Inspection",
                filters={"vehicle": vehicle},
                fields=["name"],
                limit=1
            )
            if not safety_inspection:
                frappe.msgprint(
                    f"No Vehicle Safety Inspection found for Vehicle {vehicle}. Please create one to ensure compliance.",
                    alert=True
                )

            ts_data = {
                "doctype": "Trip Sheet",
                "vehicle": vehicle,
                "driver": driver,
                "posting_date": frappe.utils.today(),
                "starting_date_and_time": doc.start_date,
                "ending_date_and_time": doc.end_date,
                "travel_requests": [{
                    "employee_travel_request": etr_name
                }],
            }
            if safety_inspection:
                ts_data["vehicle_template"] = safety_inspection[0].name
                inspection_doc = frappe.get_doc("Vehicle Safety Inspection", safety_inspection[0].name)
                ts_data["vehicle_safety_inspection_details"] = []
                for detail in inspection_doc.vehicle_safety_inspection:
                    ts_data["vehicle_safety_inspection_details"].append({
                        "item": detail.item,
                        "fit_for_use": detail.fit_for_use,
                        "remarks": detail.remarks
                    })
            else:
                ts_data["vehicle_template"] = None
                frappe.msgprint(
                    f"No Vehicle Safety Inspection found for Vehicle {vehicle}. "
                    f"Fields vehicle_template and vehicle_safety_inspection_details will be empty in Trip Sheet.",
                    alert=True
                )

            ts = frappe.get_doc(ts_data)
            ts.insert()
            
            frappe.msgprint(
                f"Trip Sheet <a href='/app/trip-sheet/{ts.name}'>{ts.name}</a> created for Vehicle {vehicle} with Driver {driver}",
                alert=True
            )


    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))

    @frappe.whitelist()
    def validate_expected_time(self):
        """Ensure Expected Check-out Time is not earlier than Expected Check-in Time."""
        if self.expected_check_in_time and self.expected_check_out_time:
            if self.expected_check_out_time < self.expected_check_in_time:
                frappe.throw("Expected Check-out Time cannot be earlier than Expected Check-in Time.")
    @frappe.whitelist()
    def total_days_calculate(self):
        """Calculate the total number of travel days, ensuring at least one day."""
        if self.start_date and self.end_date:
            start_date = self.start_date if isinstance(self.start_date, datetime) else datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
            end_date = self.end_date if isinstance(self.end_date, datetime) else datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")

            self.total_days = 1 if start_date.date() == end_date.date() else (end_date.date() - start_date.date()).days + 1


@frappe.whitelist()
def get_batta_policy(requested_by):
    '''
    Fetch the Batta Policy for the employee's designation and return the Batta policy .
    '''
    if not requested_by:
        return

    # Fetch the employee's designation
    employee = frappe.get_doc("Employee", requested_by)
    designation = employee.designation

    # Fetch the Batta Policy for the designation
    batta_policy = frappe.get_all('Batta Policy', filters={'designation': designation}, fields=['name'])

    if batta_policy:
        return batta_policy[0]
    return None

@frappe.whitelist()
def filter_room_criteria(batta_policy_name):
    '''
    Fetch and return the room criteria for the given Batta Policy.
    '''
    if  batta_policy_name:
        room_criteria_records = frappe.db.get_all('Room Criteria Table', filters={'parent': batta_policy_name}, pluck='room_criteria')
        if room_criteria_records:
            return room_criteria_records
        else:
            return []
    else:
        return []


@frappe.whitelist()
def filter_mode_of_travel(batta_policy_name):
    '''
    Fetch and return the mode of travel for the given Batta Policy.
    '''

    # Fetch the Room Criteria based on the parent
    mode_of_travel = frappe.db.get_all('Mode of Travel Table', filters={'parent': batta_policy_name}, pluck='mode_of_travel')
    if mode_of_travel:
        return mode_of_travel
    else:
        return []

@frappe.whitelist()
def create_expense_claim(employee, travel_request, expenses):
    '''
    Create an Expense Claim from Travel Request.
    '''

    if isinstance(expenses, str):
        expenses = json.loads(expenses)

    if not expenses:
        frappe.throw(_("Please provide at least one expense item."))

    travel_doc = frappe.get_doc("Employee Travel Request", travel_request)

    expense_claim = frappe.new_doc("Expense Claim")
    expense_claim.travel_request = travel_request
    expense_claim.employee = employee
    expense_claim.approval_status = "Draft"
    expense_claim.posting_date = today()

    # Get Company and payable account
    employee_doc = frappe.get_doc("Employee", employee)
    company = employee_doc.company

    default_payable_account = frappe.get_cached_value('Company', company, 'default_payable_account')
    if not default_payable_account:
        default_payable_account = frappe.db.get_value("Account", {
            "company": company,
            "account_type": "Payable",
            "is_group": 0
        }, "name")

    if not default_payable_account:
        frappe.throw(_("Please set a Default Payable Account in Company {0}").format(company))

    expense_claim.payable_account = default_payable_account

    for expense in expenses:
        amount = expense.get("amount")
        if amount in [None, ""]:
            frappe.throw(_("Expense Amount is required for all items."))

        expense_entry = {
            "amount": amount,
            "expense_date": expense.get("expense_date"),
            "expense_type": expense.get("expense_type"),
            "description": expense.get("description")
        }
        expense_claim.append("expenses", expense_entry)

    expense_claim.total_claimed_amount = sum((item.amount or 0) for item in expense_claim.expenses)
    expense_claim.save()

    frappe.msgprint(
        _('Expense Claim Created: <a href="{0}">{1}</a>').format(get_url_to_form("Expense Claim", expense_claim.name), expense_claim.name),
        alert=True,indicator='green')

    return expense_claim.name


@frappe.whitelist()
def get_expense_claim_html(doc):
    """
    Render HTML showing Expense Claims and their 'expenses'  for a given Travel Request.
    
    Args:
        doc (str): The name/ID of the Travel Request document.
    
    Returns:
        dict: A dictionary containing the rendered HTML.
    """
    if not doc:
        frappe.throw(_("Travel Request ID is required."))

    expense_claims = frappe.get_all(
        "Expense Claim",
        filters={"travel_request": doc},
        fields=["name", "employee", "total_claimed_amount", "posting_date", "status"]
    )

    full_claims = []
    for claim in expense_claims:
        ec_doc = frappe.get_doc("Expense Claim", claim.name)
        expenses = sorted(
            ec_doc.expenses,
            key=lambda x: x.expense_date,
            reverse=True
        )
        full_claims.append({
            "name": ec_doc.name,
            "employee": ec_doc.employee,
            "posting_date": ec_doc.posting_date,
            "status": ec_doc.status,
            "url": frappe.utils.get_url_to_form("Expense Claim", claim.name),
            "expenses": [
                {
                    "expense_date": row.expense_date,
                    "expense_type": row.expense_type,
                    "default_account": row.default_account,
                    "description": row.description,
                    "amount": row.amount,
                    "sanctioned_amount": row.sanctioned_amount,
                }
                for row in expenses
            ]
        })

    html = frappe.render_template(
        "beams/doctype/employee_travel_request/expense_claim.html",
        {"expense_claims": full_claims}
    )

    return {"html": html}

@frappe.whitelist()
def get_permission_query_conditions(user):
    """
    Returns SQL query conditions for controlling access to Employee Travel Requests.

    Rules:
    - "Admin" and "System Manager": full access.
    - "HOD": requests from employees in their department.
    - Employees: their own requests.
    - Others: no access.

    Args:
        user (str): User ID. Defaults to current session user.

    Returns:
        str: SQL conditions or None for unrestricted access.
    """
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "Admin" in user_roles or "System Manager" in user_roles:
        return None

    conditions = []

    if "HOD" in user_roles:
        department = frappe.db.get_value("Employee", {"user_id": user}, "department")
        if department:
            conditions.append(f"""
                EXISTS (
                    SELECT 1 FROM `tabEmployee` e
                    WHERE e.name = `tabEmployee Travel Request`.requested_by
                    AND e.department = '{department}'
                )
            """)

    employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if employee_id:
        conditions.append(f"`tabEmployee Travel Request`.requested_by = '{employee_id}'")

    if not conditions:
        return "1=0"

    return " OR ".join(f"({cond.strip()})" for cond in conditions)
