import frappe

def validate(doc, method=None):
	"""
	Check if the employee has another shift assignment on the same day.
	If yes, set roster_type to 'Double Shift'.
	"""
	if not doc.employee or not doc.start_date:
		return

	# Check for existing assignments on the same day for the same employee
	existing_assignments = frappe.get_all("Shift Assignment", filters={
		"employee": doc.employee,
		"start_date": doc.start_date,
		"name": ["!=", doc.name],
		"docstatus": ["!=", 2]
	})

	if existing_assignments:
		doc.roster_type = "Double Shift"
