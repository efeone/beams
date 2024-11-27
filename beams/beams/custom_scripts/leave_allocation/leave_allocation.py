import frappe
from frappe.utils import today, add_days
from datetime import datetime

def create_new_log_on_update(doc, method):
    """
    Automatically creates or updates Compensatory Leave Log based on Leave Allocation changes.
    Only proceeds if the employee has a Shift Assignment with roster_type = 'Double shift'.
    """
    # Fetch the previous document state
    previous_doc = doc.get_doc_before_save()

    # Handle updates to Leave Allocation, checking if dates or allocated leaves have changed
    if previous_doc.to_date != doc.to_date or previous_doc.new_leaves_allocated != doc.new_leaves_allocated:
        start_date = doc.from_date
        end_date = doc.to_date

        # If dates are not set manually, fallback to checkin data
        if not start_date or not end_date:
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

            # Set a default end_date as 30 days after the start_date
            end_date = add_days(start_date, 30)

        # Verify Shift Assignment with roster_type 'OT'
        shift_assignment = frappe.db.sql("""
            SELECT name FROM `tabShift Assignment`
            WHERE employee = %s
              AND roster_type = 'Double Shift'
              AND %s BETWEEN start_date AND end_date
        """, (doc.employee, start_date), as_dict=True)

        if not shift_assignment:
            return  # Exit if no matching Shift Assignment exists

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


def create_new_compensatory_leave_log(doc, method):
    """
    Automatically creates a Compensatory Leave Log based on Leave Allocation data.
    Only proceeds if the employee has a Shift Assignment with roster_type = 'Double Shift'.
    """
    start_date = doc.from_date
    end_date = doc.to_date

    # If dates are not set manually, fallback to checkin data
    if not start_date or not end_date:
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

        # Set a default end_date as 30 days after the start_date
        end_date = add_days(start_date, 30)

    # Verify Shift Assignment with roster_type 'OT'
    shift_assignment = frappe.db.sql("""
        SELECT name FROM `tabShift Assignment`
        WHERE employee = %s
          AND roster_type = 'Double Shift'
          AND %s BETWEEN start_date AND end_date
    """, (doc.employee, start_date), as_dict=True)

    if not shift_assignment:
        return  # Exit if no matching Shift Assignment exists

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



def validate(doc, method):
    """
    Validation for Leave Allocation DocType

    This function validates that the selected leave type in the Leave Allocation
    DocType is permitted for the employee based on their gender. If the leave type
    is listed in the Gender Leave Type Mapping, it validates whether the leave type
    is allowed for the employee's gender. If the leave type is not listed in the mapping,
    no validation is performed.
    """
    
    employee_gender = frappe.db.get_value("Employee", doc.employee, "gender")
    
    if not employee_gender:
        frappe.throw(f"Gender not found for Employee {doc.employee}. Please ensure gender is set in the Employee record.")

    is_leave_type_mapped = frappe.db.exists("Gender Leave Type Mapping", {"leave_type": doc.leave_type})

    
    if is_leave_type_mapped:
        is_valid_mapping = frappe.db.exists(
            "Gender Leave Type Mapping",
            {
                "leave_type": doc.leave_type,
                "gender": employee_gender,
            }
        )

        
        if not is_valid_mapping:
            frappe.throw(
                f"The Selected Leave Type '{doc.leave_type}' is not permitted for Employee {doc.employee} "
                f"with gender '{employee_gender}'. Please select a valid leave type."
            )
    else:
        frappe.throw(f"The Selected Leave Type is not allowed")        

