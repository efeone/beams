import frappe
from frappe import _
from frappe.utils import add_days, nowdate
from frappe.utils import getdate
from hrms.hr.doctype.leave_application.leave_application import get_leave_details

def validate(doc, method):
    validate_notice_period(doc)
    validate_leave_advance_days(doc.from_date, doc.leave_type)
    validate_sick_leave(doc)
    validate_leave_application(doc)

@frappe.whitelist()
def validate_leave_advance_days(from_date, leave_type):
    '''
    Validates the `from_date` for Leave based on the minimum advance days specified in the Leave Type.
    If min_advance_days is 0 or not provided, no validation is performed.
    '''
    if not leave_type:
        frappe.throw(_("Leave Type is required."))

    leave_type_doc = frappe.get_doc("Leave Type", leave_type)
    min_advance_days = leave_type_doc.min_advance_days or 0

    if min_advance_days == 0:
        return

    current_date = nowdate()
    min_allowed_date = add_days(current_date, min_advance_days)

    if from_date and from_date < min_allowed_date:
        frappe.throw(
            _("The From Date must be at least {0} days from today for the selected Leave Type.")
            .format(min_advance_days)
        )

def validate_sick_leave(doc):
    '''
    Validation for Sick Leave Application:
    - Check if the leave_type in Leave Application has the is_sick_leave field checked.
    - Validate medical certificate requirement based on the 'medical_leave_required' threshold in Leave Type.
    '''
    # Get leave type details
    leave_type_details = frappe.db.get_value("Leave Type",doc.leave_type,["is_sick_leave", "medical_leave_required"],as_dict=True)

    if leave_type_details and leave_type_details.is_sick_leave:
        if leave_type_details.medical_leave_required and doc.total_leave_days > leave_type_details.medical_leave_required:
            if not doc.medical_certificate:
                frappe.throw(_("Medical certificate is required for sick leave exceeding {0} days.").format(leave_type_details.medical_leave_required))

def validate_leave_application(doc):
    """
    Validates the leave application based on the penalty leave type in Employment Type doctype
    only if:
    1. The employee is marked absent on the leave application dates.
    2. The posting date of the leave application is after the absent date(s).
    """
    # Fetch all absences for the employee within the leave application date range
    absences = frappe.get_all(
        'Attendance',
        filters={
            "employee": doc.employee,
            "status": "Absent",
            "attendance_date": ["between", [doc.from_date, doc.to_date]],
            "docstatus": 1,
        },
        fields=["attendance_date"],
    )
    
    valid_absent_dates = [
        absence["attendance_date"]
        for absence in absences
        if frappe.utils.getdate(doc.posting_date) >= frappe.utils.getdate(absence["attendance_date"])
    ]

    if valid_absent_dates:
        # Fetch employee details
        employee_name = doc.employee_name
        employment_type = frappe.get_value("Employee", doc.employee, "employment_type")

        if not employment_type:
            frappe.throw("Employment type is not set for Employee: {0}".format(employee_name))

        penalty_leave_type = frappe.get_value('Employment Type', employment_type, 'penalty_leave_type')

        if not penalty_leave_type:
            # If penalty_leave_type is not set, allow only 'Leave Without Pay'
            if doc.leave_type != 'Leave Without Pay':
                frappe.throw(
                    "As per the penalty policy, only 'Leave Without Pay' can be applied for Employee: <b>{0}</b>".format(
                        employee_name
                    )
                )
            return

        # Fetch leave details using the get_leave_details function
        leave_details = get_leave_details(doc.employee, doc.posting_date)
        leave_allocations = leave_details.get('leave_allocation', {})
        lwps = leave_details.get('lwps', [])

        # Check if penalty leave type exists in the leave allocation
        if penalty_leave_type not in leave_allocations:
            if doc.leave_type not in lwps:
                frappe.throw(
                    "As per the penalty policy, only 'Leave Without Pay' can be applied for Employee: <b>{0}</b>".format(
                        employee_name
                    )
                )
            return

        # Retrieve necessary data from leave details
        leave_data = leave_allocations.get(penalty_leave_type)
        available_leaves = leave_data.get("remaining_leaves", 0)

        # Check if the leave balance is exhausted
        if available_leaves <= 0:
            if doc.leave_type not in lwps:
                frappe.throw(
                    "Available balance for '<b>{0}</b>' is 0. "
                    "As per the penalty policy, only 'Leave Without Pay' can be applied for Employee: <b>{1}</b>".format(
                        penalty_leave_type, employee_name
                    )
                )
        elif available_leaves < doc.total_leave_days:
            frappe.throw(
                "Insufficient leave balance for '<b>{0}</b>'. "
                "You have only '<b>{1}</b>' leaves remaining.".format(penalty_leave_type, available_leaves)
            )
        else:
            if doc.leave_type != penalty_leave_type:
                frappe.throw(
                    "As per the penalty policy, only '<b>{0}</b>' can be applied for Employee: <b>{1}</b>".format(
                        penalty_leave_type, employee_name
                    )
                )

def validate_notice_period(doc):
    '''
        Validate that an employee cannot take certain leave types during notice period
        if the leave type is not allowed in the notice period.
    '''
    resignation_letter_date = frappe.db.get_value("Employee", doc.employee, "resignation_letter_date")
    if resignation_letter_date:
        resignation_letter_date = getdate(resignation_letter_date)
        from_date = getdate(doc.from_date)
        if from_date >= resignation_letter_date:
            leave_type = frappe.db.get_value("Leave Type", doc.leave_type, "allow_in_notice_period")
            if not leave_type:
                frappe.throw(_("You are not allowed to apply for {0} during the <b>Notice Period</b>.").format(frappe.bold(doc.leave_type)))
