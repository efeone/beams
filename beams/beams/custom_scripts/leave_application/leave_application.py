import frappe
def validate_leave_application(doc, method):
    '''
    Validates the leave application based on the penalty leave type set in the HR settings.
    '''
    penalty_leave_type = frappe.get_single('Beams HR Settings').penalty_leave_type

    # Get total allocated leaves for the penalty leave type
    total_allocated = frappe.db.get_value(
        'Leave Allocation', {'employee': doc.employee, 'leave_type': penalty_leave_type}, 'total_leaves_allocated'
    ) or 0

    # Calculate leaves used for the penalty leave type
    leaves_used = frappe.db.sql("""
        SELECT SUM(total_leave_days)
        FROM `tabLeave Application`
        WHERE employee = %s AND leave_type = %s AND docstatus = 1
    """, (doc.employee, penalty_leave_type))[0][0] or 0

    # Remaining leave balance
    leave_balance = total_allocated - leaves_used

    # If no balance left, enforce Leave Without Pay
    if leave_balance == 0 and doc.leave_type != 'Leave Without Pay':
        frappe.throw('Your \'{0}\' leave balance is exhausted. Apply for \'Leave Without Pay\'.'.format(penalty_leave_type))

    # If penalty leave balance exists, restrict applying for other leave types
    if leave_balance > 0 and doc.leave_type != penalty_leave_type:
        frappe.throw('You can only apply for \'{0}\' leave. Remaining balance: {1}.'.format(penalty_leave_type, leave_balance))
