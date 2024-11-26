import frappe
from frappe import _
from frappe.utils import add_days, nowdate

@frappe.whitelist()
def validate_leave_type(doc, method):
    validate_leave_advance_days(doc.from_date, doc.leave_type)

@frappe.whitelist()
def validate_leave_advance_days(from_date, leave_type):
    '''
    Validates the `from_date` for Leave based on the minimum advance days specified in the Leave Type.
    '''
    if not leave_type:
        frappe.throw(_("Leave Type is required."))

    # Fetch the Leave Type document
    leave_type_doc = frappe.get_doc("Leave Type", leave_type)

    # Get the minimum advance days for the leave type
    min_advance_days = leave_type_doc.min_advance_days or 0

    # Get the current date and calculate the minimum allowed from_date
    current_date = nowdate()
    min_allowed_date = add_days(current_date, min_advance_days)

    # Check if the provided from_date is before the minimum allowed date
    if from_date and from_date < min_allowed_date:
        frappe.throw(
            _("The From Date must be at least {0} days from today for the selected Leave Type.")
            .format(min_advance_days)
        )


@frappe.whitelist()
def validate_leave_application(doc, method):
    """
    Validation for Leave Application:
    - Check if the leave_type in Leave Application has the is_sick_leave field checked.
    - Validate medical certificate requirement based on the 'medical_leave_required' threshold in Leave Type.
    """
    leave_type_details = frappe.db.get_value("Leave Type", doc.leave_type, ["is_sick_leave", "medical_leave_required"], as_dict=True)
    if leave_type_details and leave_type_details.is_sick_leave:
        if leave_type_details.medical_leave_required and doc.total_leave_days > leave_type_details.medical_leave_required:
            if not doc.medical_certificate:
                frappe.throw(_("Medical certificate is required for sick leave exceeding {0} days.").format(leave_type_details.medical_leave_required))
