from datetime import timedelta
import frappe
from frappe.utils import getdate, nowdate
from frappe.model.document import Document


class CompensatoryLeaveLog(Document):
    def validate(self):
        '''Validate the compensatory leave dates'''
        if self.start_date and self.end_date and getdate(self.end_date) < getdate(self.start_date):
            frappe.throw('End Date cannot be before Start Date')

@frappe.whitelist()
def process_expired_compensatory_leaves(self=None, method=None):
    '''This method check list of CLL and allocated leaves and leave applications and reduce
        allocated leaves if it is used or expires if unused.'''

    thirty_days_ago = getdate(nowdate()) - timedelta(days=30)

    # Fetch compensatory leave logs within the last 30 days
    compensatory_leaves = frappe.get_all(
        'Compensatory Leave Log',
        filters={
            'end_date': ['>=', thirty_days_ago],
            'leave_type': 'Compensatory Off',
        }
    )

    reduced_count = 0
    expired_count = 0

    # Iterate over each compensatory leave record
    for leave in compensatory_leaves:
        doc = frappe.get_doc('Compensatory Leave Log', leave.name)

        # Skip if no linked leave allocation exists
        if not doc.leave_allocation:
            continue

        allocation = frappe.get_doc('Leave Allocation', doc.leave_allocation)

        # Skip if the linked Leave Allocation is not submitted
        if allocation.docstatus != 1:
            continue

        # Check for overlapping leave applications
        leave_applications = frappe.get_all(
            'Leave Application',
            filters={
                'employee': doc.employee,
                'leave_type': 'Compensatory Off',
                'from_date': ['<=', doc.end_date],
                'to_date': ['>=', doc.start_date],
                'docstatus': 1
            }
        )

        current_balance = allocation.total_leaves_allocated

        if leave_applications:
            # Reduce the leave allocation for overlapping leave applications
            for application in leave_applications:
                leave_application = frappe.get_doc('Leave Application', application.name)
                total_leave_days = leave_application.total_leave_days
                days_to_reduce = min(total_leave_days, current_balance)

                if days_to_reduce > 0:
                    new_balance = current_balance - days_to_reduce
                    frappe.db.set_value('Leave Allocation', allocation.name, {'total_leaves_allocated': new_balance})
                    reduced_count += days_to_reduce

        elif doc.end_date <= thirty_days_ago and current_balance > 0:
            # Expire compensatory leave if no application exists
            days_to_expire = min(current_balance, 1)  # Assuming 1 day per log
            new_balance = current_balance - days_to_expire
            frappe.db.set_value('Leave Allocation', allocation.name, {'total_leaves_allocated': new_balance})
            expired_count += days_to_expire

    return
#
