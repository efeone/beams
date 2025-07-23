import frappe
from frappe.desk.form.assign_to import add as add_assign

@frappe.whitelist()
def create_exit_clearance(doc, method=None):
	'''
	Create Employee Exit Clearance records and assign them to the respective department heads.
	'''

	if isinstance(doc, str):
		doc = frappe.get_doc(frappe.parse_json(doc))
	elif isinstance(doc, dict):
		doc = frappe.get_doc(doc)

	designation = doc.get("designation") or frappe.db.get_value("Employee", doc.employee, "designation")
	boarding_begins_on = doc.boarding_begins_on
	relieving_date = frappe.db.get_value("Employee", doc.employee, "relieving_date")

	for row in doc.employee_clearance:
		department = row.department
		if not department:
			continue

		duplicates = [r for r in doc.employee_clearance if r.department == department and r.name != row.name]
		if duplicates:
			frappe.throw(f"Department '{department}' is already selected in another row.")

		if row.employee_exit_clearance:
			continue

		# Check if Employee Exit Clearance already exists
		existing_clearance = frappe.db.exists("Employee Exit Clearance", {
			"employee": doc.employee,
			"department": department
		})
		if existing_clearance:
			row.employee_exit_clearance = existing_clearance
			row.status = "Pending"
			continue

		department_head = frappe.db.get_value("Department", department, "head_of_department")
		department_head_user = frappe.db.get_value("Employee", department_head, "user_id") if department_head else None

		clearance = frappe.new_doc("Employee Exit Clearance")
		clearance.employee = doc.employee
		clearance.clearance_for_department = department
		clearance.status = "Pending"
		clearance.assigned_to = department_head_user or ""
		clearance.designation = designation or ""
		clearance.relieving_date = relieving_date or None
		clearance.employee_separation_begins_on = boarding_begins_on or None
		clearance.insert(ignore_permissions=True)

		# ToDo Assignment to Department Head
		if department_head_user:
			add_assign({
				"assign_to": [department_head_user],
				"doctype": "Employee Exit Clearance",
				"name": clearance.name,
				"description": f"Please review and complete the exit clearance for {doc.employee} in {department}."
			})

		row.employee_exit_clearance = clearance.name
		frappe.db.set_value("Employee Clearance", row.name, "employee_exit_clearance", clearance.name)
		row.status = "Pending"

