# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days


class CompensatoryLeaveLog(Document):
    pass

@frappe.whitelist()
def expire_leave_allocation():
    '''
    Expire leave allocations for all compensatory leave logs if no leave application exists.
    '''
    today = getdate(nowdate())

    # Fetch all compensatory leave logs that are older than 30 days
    logs = frappe.get_all('Compensatory Leave Log', filters={
        'end_date': ('<=', today)
    })

    for log in logs:
        log_doc = frappe.get_doc('Compensatory Leave Log', log.name)

        # Fetch all leave applications for the same employee and leave type that are approved
        leave_application = frappe.get_all('Leave Application', filters={
            'employee': log_doc.employee,
            'leave_type': log_doc.leave_type,
            'docstatus': 1  # Approved leave applications
        })

        # Check if there is any leave application that overlaps with the compensatory leave
        overlap_found = False
        for application in leave_application:
            leave_app_doc = frappe.get_doc('Leave Application', application.name)
            leave_from = getdate(leave_app_doc.from_date)
            leave_to = getdate(leave_app_doc.to_date)

            # Check if the leave application period overlaps with the compensatory leave log period
            if (leave_from <= log_doc.end_date and leave_to >= log_doc.start_date):
                overlap_found = True
                break

        # If there is an overlap, do not reduce leave
        if overlap_found:
            continue
        else:
            # Fetch the leave allocation and reduce the leave
            leave_allocation = frappe.get_all('Leave Allocation', filters={
                'employee': log_doc.employee,
                'leave_type': log_doc.leave_type
            })

            if leave_allocation:
                leave_allocation_doc = frappe.get_doc('Leave Allocation', leave_allocation[0].name)

                # Ensure we are not reducing the leave if it has already been reduced to 0 or below
                if leave_allocation_doc.new_leaves_allocated > 0:
                    leave_allocation_doc.new_leaves_allocated -= 1  # Decrease one leave from allocation
                    leave_allocation_doc.save()
