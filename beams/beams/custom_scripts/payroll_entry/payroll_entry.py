import frappe
from frappe.utils import add_months, get_first_day, get_last_day, getdate

def set_previous_month_dates(doc, method=None):
	"""Auto-set start_date and end_date to PREVIOUS month based on posting_date"""
	if doc.posting_date and doc.payroll_frequency == 'Monthly':
		if not doc.start_date or not doc.end_date:
			# Get the first day of the previous month
			posting_date = getdate(doc.posting_date)
			prev_month_date = add_months(posting_date, -1)

			doc.start_date = get_first_day(prev_month_date)
			doc.end_date = get_last_day(prev_month_date)
