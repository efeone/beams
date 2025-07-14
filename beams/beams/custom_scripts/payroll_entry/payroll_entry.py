import frappe
from frappe.utils import add_months, get_first_day, get_last_day, getdate

def set_previous_month_dates(doc, method=None):
    """Auto-set start_date and end_date to PREVIOUS month based on posting_date"""
    
    if not doc.posting_date:
        return
    
    # Convert posting_date to date object
    posting_date = getdate(doc.posting_date)
    
    # Get PREVIOUS month's first and last day
    prev_month_date = add_months(posting_date, -1)
    start_date = get_first_day(prev_month_date)
    end_date = get_last_day(prev_month_date)
    
    # Set the dates to previous month
    doc.start_date = start_date
    doc.end_date = end_date 
