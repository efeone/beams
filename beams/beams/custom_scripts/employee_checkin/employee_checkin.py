import frappe
from frappe.utils import add_days, today
from datetime import datetime
from frappe.utils import nowdate, get_datetime
from frappe import _ 
from frappe.utils import get_url_to_form 


def handle_employee_checkin_out(doc, method):
    """
    Handles Employee Checkin with type OUT:
    - Creates or updates Leave Allocation.
    - Triggers Compensatory Leave Log creation in Leave Allocation logic.
    """
    if doc.log_type != "OUT":
        return

    # Fetch Compensatory Leave Type
    compensatory_leave_type = frappe.db.get_single_value("Beams HR Settings", "compensatory_leave_type")
    if not compensatory_leave_type:
        return

    # Parse time from the Employee Checkin log
    doc_time = datetime.strptime(doc.time, "%Y-%m-%d %H:%M:%S") if isinstance(doc.time, str) else doc.time
    start_date = doc_time.date()
    end_date = add_days(start_date, 30)
    
    # Use check-out date to verify shift assignment
    shift_assignment = frappe.db.sql("""
        SELECT name FROM `tabShift Assignment`
        WHERE employee = %s
          AND roster_type = 'Double Shift'
          AND %s BETWEEN start_date AND end_date
    """, (doc.employee, start_date), as_dict=True)

    if not shift_assignment:
        return

    # Fetch Leave Allocation
    leave_allocation = frappe.get_all(
        "Leave Allocation",
        filters={"employee": doc.employee, "leave_type": compensatory_leave_type},
        fields=["name", "to_date", "new_leaves_allocated"],
        limit=1
    )

    if leave_allocation:
        # Update existing Leave Allocation
        allocation = frappe.get_doc("Leave Allocation", leave_allocation[0].name)
        if allocation.to_date < end_date:
            allocation.to_date = end_date
        allocation.new_leaves_allocated += 1
        allocation.flags.ignore_permissions = True
        allocation.save()
    else:
        # Create new Leave Allocation
        leave_allocation_doc = frappe.new_doc("Leave Allocation")
        leave_allocation_doc.update({
            "employee": doc.employee,
            "leave_type": compensatory_leave_type,
            "from_date": start_date,
            "to_date": end_date,
            "new_leaves_allocated": 1,
        })
        leave_allocation_doc.insert(ignore_permissions=True)
        leave_allocation_doc.submit()
        
    allocation_name = allocation.name if leave_allocation else leave_allocation_doc.name

    frappe.msgprint(
        _('Double Shift found for <b>{employee}</b>.<br>'
          'Compensatory Leave has been <b>allocated</b>: <a href="{url}">{name}</a>').format(
            employee=doc.employee,
            url=get_url_to_form("Leave Allocation", allocation_name),
            name=allocation_name
        ),alert=True,indicator='green')

def set_hd_agent_active_status(doc, method=None):

    '''Update HD Agent's active status based on today's latest employee check-in'''

    employee = doc.employee

    # Get user linked to the employee
    user = frappe.db.get_value("Employee", {"name": employee}, "user_id")

    if not user:
        return

    start = get_datetime(nowdate() + " 00:00:00")
    end = get_datetime(nowdate() + " 23:59:59")

    # Get the latest check-in today
    latest_checkin = frappe.db.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [start, end]]
        },
        fields=["name", "log_type", "time"],
        order_by="time desc",
        limit=1
    )

    if latest_checkin:
        latest_log_type = latest_checkin[0].log_type
        new_status = 1 if latest_log_type == "IN" else 0
    else:
        # No check-ins today
        new_status = 0

    # Update HD Agent status
    if frappe.db.exists("HD Agent", {"user": user}):
        frappe.db.set_value("HD Agent", {"user": user}, "is_active", new_status)

