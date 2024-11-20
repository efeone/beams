import frappe
from frappe.utils import today, add_days
from datetime import datetime

def create_new_log_on_update(doc, method):
    """
    Automatically creates or updates Compensatory Leave Log based on Leave Allocation changes,
    but uses Employee Checkin data for date calculations.
    """
    # Fetch the previous document state
    previous_doc = doc.get_doc_before_save()

    # Handle updates to Leave Allocation, checking if dates or allocated leaves have changed
    if previous_doc.to_date != doc.to_date or previous_doc.new_leaves_allocated != doc.new_leaves_allocated:
        # Fetch the latest Employee Checkin log for the employee (log_type = OUT)
        checkin_data = frappe.db.get_all(
            "Employee Checkin",
            filters={"employee": doc.employee, "log_type": "OUT"},
            fields=["time"],
            order_by="time desc",  # Get the latest "OUT" log
            limit=1
        )

        if not checkin_data:
            frappe.throw(f"No checkin data found for employee {doc.employee}.")

        # If time is already a datetime object, use it directly
        doc_time = checkin_data[0].time

        # Extract the date directly from the datetime object
        start_date = doc_time.date() if isinstance(doc_time, datetime) else datetime.strptime(doc_time, "%Y-%m-%d %H:%M:%S").date()

        end_date = add_days(start_date, 30)  # Add 30 days to the start date

        # Create or update the Compensatory Leave Log
        log_doc = frappe.new_doc("Compensatory Leave Log")
        log_doc.update({
            "employee": doc.employee,
            "employee_name": doc.employee_name,
            "leave_type": doc.leave_type,
            "leave_allocation": doc.name,
            "start_date": start_date,
            "end_date": end_date,
        })
        log_doc.insert()

    frappe.db.commit()


def create_new_compensatory_leave_log(doc, method):
    """
    Automatically creates a Compensatory Leave Log based on Leave Allocation data,
    using Employee Checkin data for date calculations.
    """
    # Fetch the latest Employee Checkin log for the employee (log_type = OUT)
    checkin_data = frappe.db.get_all(
        "Employee Checkin",
        filters={"employee": doc.employee, "log_type": "OUT"},
        fields=["time"],
        order_by="time desc",  # Get the latest "OUT" log
        limit=1
    )

    if not checkin_data:
        frappe.throw(f"No checkin data found for employee {doc.employee}.")

    # If time is already a datetime object, use it directly
    doc_time = checkin_data[0].time

    # Extract the date directly from the datetime object
    start_date = doc_time.date() if isinstance(doc_time, datetime) else datetime.strptime(doc_time, "%Y-%m-%d %H:%M:%S").date()

    end_date = add_days(start_date, 30)  # Add 30 days to the start date

    # Create the Compensatory Leave Log
    log_doc = frappe.new_doc("Compensatory Leave Log")
    log_doc.update({
        "employee": doc.employee,
        "employee_name": doc.employee_name,
        "leave_type": doc.leave_type,
        "leave_allocation": doc.name,
        "start_date": start_date,
        "end_date": end_date,
    })
    log_doc.insert()

    frappe.db.commit()
