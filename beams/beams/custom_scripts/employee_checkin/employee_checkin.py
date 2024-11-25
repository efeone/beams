import frappe
from frappe.utils import add_days, today
from datetime import datetime

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
        frappe.throw("Compensatory Leave Type is not configured in Beams HR Settings.")

    # Parse time from the Employee Checkin log
    doc_time = datetime.strptime(doc.time, "%Y-%m-%d %H:%M:%S") if isinstance(doc.time, str) else doc.time
    start_date = doc_time.date()
    end_date = add_days(start_date, 30)
    today_date = today()

    # Verify Shift Assignment with roster_type 'OT'
    shift_assignment = frappe.db.sql("""
        SELECT name FROM `tabShift Assignment`
        WHERE employee = %s
          AND roster_type = 'Double Shift'
          AND %s BETWEEN start_date AND end_date
    """, (doc.employee, today_date), as_dict=True)

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
        leave_allocation_doc.insert()
        leave_allocation_doc.submit()
