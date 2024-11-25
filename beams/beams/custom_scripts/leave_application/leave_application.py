import frappe
from frappe import _
from frappe.utils import add_days, nowdate

def validate_leave_type(doc, method):
    validate_casual_leave_application(doc.from_date, doc.leave_type)

@frappe.whitelist()
def validate_casual_leave_application(from_date, leave_type):
    '''
    Validates the `from_date` for Casual Leave based on the minimum advance days specified in the Leave Type.
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
