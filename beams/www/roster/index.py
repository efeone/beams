import frappe

def get_context(context):
	'''
		Initializes the context with job applicant details if the applicant ID is valid.
		args:
			context (dict)
		Return : None
	'''
	context.no_cache = 1

@frappe.whitelist()
def get_shift_assignments(from_date, to_date, department=None):
	'''
		Fetches the shift assignments for the current user and returns them as a list of dictionaries.
		Return : List of dictionaries containing shift assignment details
	'''
	required_fields = ['shift_type', 'employee', 'employee_name', 'start_date']
	filters = {
		'start_date': ['between', [from_date, to_date]],
		'status': 'Active',
		'docstatus': 1
	}
	if department:
		filters['department'] = department
	shift_assignments = frappe.db.get_all('Shift Assignment', filters=filters, fields=required_fields)
	return shift_assignments

@frappe.whitelist()
def create_shift_assignment(employee, shift_type, shift_date):
	'''
		Creates a new shift assignment for the specified employee, shift type, and start date.
		args:
			employee (str): The employee for whom the shift assignment is to be created.
			shift_type (str): The type of shift to be assigned.
			shift_date (str): The date of the shift assignment in 'YYYY-MM-DD' format.
		Return : None
	'''
	shift_assignment = frappe.get_doc({
		'doctype': 'Shift Assignment',
		'employee': employee,
		'shift_type': shift_type,
		'start_date': shift_date,
		'end_date': shift_date
	})
	shift_assignment.insert(ignore_permissions=True)
	shift_assignment.submit()
	return shift_assignment.name

@frappe.whitelist()
def cancel_shift_assignment(employee, shift_type, shift_date):
	'''
		Cancels an existing shift assignment for the specified employee, shift type, and start date.
		args:
			employee (str): The employee for whom the shift assignment is to be cancelled.
			shift_type (str): The type of shift to be cancelled.
			shift_date (str): The date of the shift assignment in 'YYYY-MM-DD' format.
		Return : None
	'''
	shift_assignment = frappe.db.get_value('Shift Assignment', {
		'employee': employee,
		'shift_type': shift_type,
		'start_date': shift_date,
		'status': 'Active',
		'docstatus': 1
	}, 'name')
	if shift_assignment:
		doc = frappe.get_doc('Shift Assignment', shift_assignment)
		doc.cancel()
	return shift_assignment

@frappe.whitelist()
def get_employees(department=None):
	'''
		Fetches the list of employees based on the specified department.
		args:
			department (str, optional): The department to filter employees by. If None, all employees are returned.
		Return : List of dictionaries containing employee details
	'''
	filters = {'status': 'Active'}
	if department:
		filters['department'] = department
	employees = frappe.db.get_all('Employee', filters=filters, fields=['name', 'employee_name'])
	return employees

@frappe.whitelist()
def get_departments():
	'''
		Fetches the list of departments.
		Return : List of dictionaries containing department details
	'''
	filters = {
		'is_group': 0
	}
	departments = frappe.db.get_list('Department', 
		filters=filters,
		fields=['name', 'department_name'], 
		order_by='department_name', 
		limit_page_length=100
	)
	return departments
