# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url_to_form, today, getdate
from frappe.utils import nowdate
from beams.beams.doctype.trip_sheet.trip_sheet import get_last_odometer
from frappe.utils.user import get_users_with_role
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils import get_datetime
import frappe
from frappe import get_roles


class EmployeeTravelRequest(Document):

	def before_insert(self):
		self.set_from_bureau_flag()

	def set_from_bureau_flag(self):
		"""
		Sets the 'from_bureau' flag to 1 if the creating user has the
		'Bureau User' role.
		"""
		user = frappe.session.user
		if "Bureau User" in frappe.get_roles(user):
			self.from_bureau = 1

		self.set_bureau_flag()

	def validate_reason_reject(self):
		old_doc = self.get_doc_before_save()

		if old_doc and old_doc.workflow_state != self.workflow_state:

			rejection_states = ["Rejected", "Rejected by Coordinator"]

			if self.workflow_state in rejection_states and not self.reason_for_rejection:
				frappe.throw("Reason for Rejection is required when rejecting this request.")


	def validate(self):
		self.validate_reason_reject()
		self.validate_dates()
		self.validate_expected_time()
		self.total_days_calculate()

	def before_save(self):
		self.validate_posting_date()
		self.check_management_employee()
		if not self.requested_by:
			return

		# Fetch the Batta Policy for the employee
		batta_policy = get_batta_policy(self.requested_by)
		if batta_policy:
			self.batta_policy = batta_policy.get("name")

	def on_submit(self):
		self.create_notification_from_approval()
		self.create_attendance_requests()
		if self.workflow_state == "Approved":
			self.create_missing_trip_sheets_for_etr()

	def on_update(self):
		self.create_todo_for_hod()

	@frappe.whitelist()
	def validate_dates(self):
		if self.start_date and self.end_date:
			if self.start_date > self.end_date:
				frappe.throw("End Date cannot be earlier than Start Date.")
				

	def on_update_after_submit(self):
		# Trigger only when state becomes Approved
		if self.workflow_state != "Approved":
			return

		# Validation: Rejection reason must be empty when approved
		if self.reason_for_rejection:
			frappe.throw(title="Approval Error", msg="You cannot approve this request if 'Reason for Rejection' is filled.")

	def create_missing_trip_sheets_for_etr(doc):
		"""
		1.Create Trip Sheets for vehicles in the Travel Vehicle Allocation child table
			if no Trip Sheet exists yet for the current Employee Travel Request (ETR).
		2. Fetch all the employees into the Trip Sheet from the ETR including the requested_by employee.
		3. Fetch Trip Details from  Employee Travel Request fields
		"""
		etr_name = doc.name

		linked_ts_rows = frappe.get_all(
			"Employee Travel Request Details",
			filters={"employee_travel_request": etr_name},
			fields=["parent"]
		)
		ts_names = [row.parent for row in linked_ts_rows]

		existing_ts = frappe.get_all(
			"Trip Sheet",
			filters={"name": ["in", ts_names], "docstatus": ["!=", 2]},
			fields=["name", "vehicle"]
		)

		existing_vehicles_with_ts = {ts.vehicle for ts in existing_ts}

		allocations = [{
			"vehicle": row.vehicle,
			"driver": row.driver
		} for row in doc.travel_vehicle_allocation]

		if not existing_ts:
			vehicles_to_create = allocations
		else:
			vehicles_to_create = [alloc for alloc in allocations if alloc["vehicle"] not in existing_vehicles_with_ts]

		trip_sheet_columns = frappe.db.get_table_columns("Trip Sheet")

		for alloc in vehicles_to_create:
			vehicle = alloc["vehicle"]
			driver = alloc.get("driver")

			initial_odometer = get_last_odometer(vehicle)

			safety_inspection = frappe.get_all(
				"Vehicle Safety Inspection",
				filters={"vehicle": vehicle},
				fields=["name"],
				limit=1
			)

			if not safety_inspection:
				frappe.msgprint(
					f"No Vehicle Safety Inspection found for Vehicle {vehicle}. Please create one to ensure compliance.",
					alert=True
				)

			ts_data = {
				"doctype": "Trip Sheet",
				"vehicle": vehicle,
				"driver": driver,
				"posting_date": frappe.utils.today(),
				"starting_date_and_time": doc.start_date,
				"ending_date_and_time": doc.end_date,
				"initial_odometer_reading": initial_odometer,
				"travel_requests": [{
					"employee_travel_request": etr_name
				}],
			}

			if "final_odometer" in trip_sheet_columns:
				ts_data["final_odometer"] = None

			requested_by = frappe.db.get_value(
				"Employee Travel Request",
				etr_name,
				"requested_by"
			)

			travellers = frappe.get_all(
				"Traveller",
				filters={"parent": etr_name},
				pluck="employee"
			)

			employees = set(travellers)
			if requested_by:
				employees.add(requested_by)

			ts_data["employees"] = [{"employee": emp} for emp in employees]

			ts_data["trip_details"] = [{
				"departure": doc.source,
				"destination": doc.destination,
				"from_time": doc.start_date,
				"to_time": doc.end_date,
				"hrs": None,
				"distance_traveled": None,
				"remark": None
			}]

			if safety_inspection:
				ts_data["vehicle_template"] = safety_inspection[0].name
				inspection_doc = frappe.get_doc("Vehicle Safety Inspection", safety_inspection[0].name)
				ts_data["vehicle_safety_inspection_details"] = []

				for detail in inspection_doc.vehicle_safety_inspection:
					ts_data["vehicle_safety_inspection_details"].append({
						"item": detail.item,
						"fit_for_use": detail.fit_for_use,
						"remarks": detail.remarks
					})
			else:
				ts_data["vehicle_template"] = None
				frappe.msgprint(
					f"No Vehicle Safety Inspection found for Vehicle {vehicle}. "
					f"Fields vehicle_template and vehicle_safety_inspection_details will be empty in Trip Sheet.",
					alert=True
				)

			ts = frappe.get_doc(ts_data)
			ts.insert()

			frappe.msgprint(
				f"Trip Sheet <a href='/app/trip-sheet/{ts.name}'>{ts.name}</a> created for Vehicle {vehicle} with Driver {driver}",
				alert=True
			)

	def create_notification_from_approval(self):
		if self.workflow_state == "Approved":
			template_name = frappe.db.get_single_value("BEAMS Admin Settings", "employee_travel_request_approved_template")
			if not template_name:
				frappe.throw(_("Please set 'employee_travel_request_approved_template' in BEAMS Admin Settings."),title=_("Missing Template"))
			template = frappe.get_doc("Email Template", template_name)
			context = {
				"doc": self,
				"employee": self.requested_by,
				"source": self.source,
				"destination": self.destination,
			}
			subject = frappe.render_template(template.subject, context)
			email_content = frappe.render_template(template.response, context)
			department= frappe.db.get_value("Employee", self.requested_by, "department")
			hod_emp= frappe.db.get_value("Department", department, "head_of_department")
			if hod_emp:
				hod_user = frappe.db.get_value("Employee", hod_emp, "user_id")
				if hod_user:
					frappe.sendmail(recipients=frappe.db.get_value("User", hod_user, "email"), subject=subject, message=email_content)
			if self.requested_by:
				emp_user = frappe.db.get_value("Employee", self.requested_by, "user_id")
				if emp_user:
					frappe.sendmail(recipients=frappe.db.get_value("User", emp_user, "email"), subject=subject, message=email_content)


	def create_todo_for_hod(self):
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.workflow_state != self.workflow_state and  self.workflow_state == "Pending":
			department = frappe.db.get_value("Employee", self.requested_by, "department")
			hod_emp = frappe.db.get_value("Department", department, "head_of_department")
			if hod_emp:
				hod_user = frappe.db.get_value("Employee", hod_emp, "user_id")
				if hod_user:
					exists = frappe.db.exists(
						"ToDo",{
							"reference_type": "Employee Travel Request", 
							"reference_name": self.name, 
							"allocated_to": hod_user 
						},
					)
					if not exists:
						description = (
							"An employee has created a travel request for your Approval. "
							"Please review it."
						)
						add_assign(
							{
								"assign_to": [hod_user],
								"doctype": "Employee Travel Request",
								"name": self.name,
								"description": description,
							}
						)
		elif  old_doc and old_doc.workflow_state != self.workflow_state and self.workflow_state == "Approved by HOD":
			users = get_users_with_role("Admin")
			if users:
				for user in users:
					exists = frappe.db.exists(
						"ToDo",{
							"reference_type": "Employee Travel Request", 
							"reference_name": self.name, 
							"allocated_to": user,
						},
					)
					if not exists:
						description = (
							"Employee Travel Request is Approved "
							"Please review and give your approval."
						)
						add_assign(
							{
								"assign_to": [user],
								"doctype": "Employee Travel Request",
								"name": self.name,
								"description": description,
							}
						)

	def create_attendance_requests(self):
		"""
		Create attendance requests for all travellers when mark_attendance is enabled.
		Handles overlaps by creating requests only for the remaining free days.
		"""
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.workflow_state != self.workflow_state and self.workflow_state == "Approved":
			if not self.mark_attendance:
				return

			employees = []

			# Add main employee
			if self.requested_by:
				employees.append(self.requested_by)

			# Add employees from child table
			for row in self.travellers:
				if row.employee:
					employees.append(row.employee)

			# Remove duplicates and empty entries
			employees = list(set(filter(None, employees)))

			for emp in employees:
				travel_from = frappe.utils.getdate(self.start_date)
				travel_to = frappe.utils.getdate(self.end_date)

				# Get existing attendance ranges for this employee
				existing = frappe.db.sql(
					"""
					SELECT from_date, to_date
					FROM `tabAttendance Request`
					WHERE employee = %s
					AND docstatus != 2
					AND to_date >= %s
					AND from_date <= %s
					ORDER BY from_date
					""",
					(emp, travel_from, travel_to),
					as_dict=True,
				)

				free_ranges = []
				current_start = travel_from

				for e in existing:
					# If there is a gap before this existing request
					if current_start < e["from_date"]:
						free_ranges.append((current_start, frappe.utils.add_days(e["from_date"], -1)))
					# Move start beyond this overlap
					if current_start <= e["to_date"]:
						current_start = frappe.utils.add_days(e["to_date"], 1)

				# After processing all overlaps, if days remain
				if current_start <= travel_to:
					free_ranges.append((current_start, travel_to))

				# Create attendance requests for free ranges
				for f_start, f_end in free_ranges:
					if f_start <= f_end:
						attendance = frappe.get_doc({
							"doctype": "Attendance Request",
							"employee": emp,
							"from_date": f_start,
							"to_date": f_end,
							"request_type": "On Duty",
							"company": frappe.db.get_value("Employee", emp, "company"),
							"description": f"From Travel Request {self.name}",
							"reason": "On Duty"
						})
						attendance.insert(ignore_permissions=True)
						frappe.msgprint(
							f"Attendance Request created for {emp} ({f_start} → {f_end})",
							alert=True, indicator='green'
						)
	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if getdate(self.posting_date) > getdate(today()):
				frappe.throw(_("Posting Date cannot be set after today's date."))

	def validate_expected_time(self):
		"""Ensure Expected Check-out Time is not earlier than Expected Check-in Time."""
		if self.expected_check_in_time and self.expected_check_out_time:
			if self.expected_check_out_time < self.expected_check_in_time:
				frappe.throw("Expected Check-out Time cannot be earlier than Expected Check-in Time.")

	def validate_vehicle_allocation(self):
		"""Validate vehicle & driver allocation at Admin approval stage"""
		if (
			self.is_vehicle_required
			and self.workflow_state == "Approved"
			and self.mode_of_travel not in ["Train", "Plane"]
		):
			if not self.travel_vehicle_allocation:
				frappe.throw(
					title="Approval Error",
					msg="Vehicle allocation is required before Admin approval."
				)

			has_complete_allocation = any(
				allocation.vehicle and allocation.driver
				for allocation in self.travel_vehicle_allocation
			)

			if not has_complete_allocation:
				frappe.throw(
					title="Approval Error",
					msg="You must allocate driver and vehicle before Admin approval."
				)


	@frappe.whitelist()
	def total_days_calculate(self):
		"""Calculate the total number of travel days, ensuring at least one day."""
		if self.start_date and self.end_date:
			start_date = self.start_date if isinstance(self.start_date, datetime) else datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
			end_date = self.end_date if isinstance(self.end_date, datetime) else datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")

			self.total_days = 1 if start_date.date() == end_date.date() else (end_date.date() - start_date.date()).days + 1

	def check_management_employee(self):
		"""
		Set is_management_employee to 1 if the requested_by employee's user has
		the Management role or the custom role defined in BEAMS Admin Settings.
		"""

		self.is_management_employee = 0

		employee_user = frappe.db.get_value("Employee", self.requested_by, "user_id")
		if not employee_user:
			return

		role_to_check = frappe.db.get_value(
			"BEAMS Admin Settings", "BEAMS Admin Settings", "management_user_role"
		) or "Management"


		if frappe.db.exists("Has Role", {"parent": employee_user, "role": role_to_check}):
			self.is_management_employee = 1

	def set_bureau_flag(self):
		"""
		Sets `has_bureau_head_role` automatically based on:
		- Creator's roles
		- Employee's linked user's roles (via requested_by)
		"""
		creator = frappe.session.user
		if self.has_bureau_role(creator):
			self.has_bureau_head_role = 1
			return

		employee = self.requested_by
		if employee:
			emp_user = frappe.db.get_value("Employee", employee, "user_id")
			if emp_user and self.has_bureau_role(emp_user):
				self.has_bureau_head_role = 1
				return

		self.has_bureau_head_role = 0

	def has_bureau_role(self, user):
		"""
		Helper: Check whether a given User has the 'Bureau User' role.
		"""
		roles = get_roles(user)
		return "Bureau User" in roles


@frappe.whitelist()
def get_batta_policy(requested_by):
	'''
	Fetch the Batta Policy for the employee's designation and return the Batta policy .
	'''
	if not requested_by:
		return
	if frappe.db.exists("Employee", requested_by):
	# Fetch the employee's designation
		employee = frappe.get_doc("Employee", requested_by)
		designation = employee.designation

	# Fetch the Batta Policy for the designation
	batta_policy = frappe.get_all('Batta Policy', filters={'designation': designation}, fields=['name'])

	if batta_policy:
		return batta_policy[0]
	return None

@frappe.whitelist()
def filter_room_criteria(batta_policy_name):
	'''
	Fetch and return the room criteria for the given Batta Policy.
	'''
	if  batta_policy_name:
		room_criteria_records = frappe.db.get_all('Room Criteria Table', filters={'parent': batta_policy_name}, pluck='room_criteria')
		if room_criteria_records:
			return room_criteria_records
		else:
			return []
	else:
		return []


@frappe.whitelist()
def filter_mode_of_travel(batta_policy_name):
	'''
	Fetch and return the mode of travel for the given Batta Policy.
	'''

	# Fetch the Room Criteria based on the parent
	mode_of_travel = frappe.db.get_all('Mode of Travel Table', filters={'parent': batta_policy_name}, pluck='mode_of_travel')
	if mode_of_travel:
		return mode_of_travel
	else:
		return []

@frappe.whitelist()
def create_expense_claim(employee, travel_request, expenses, is_budgeted, is_budget_exceeded):
	'''
	Create an Expense Claim from Travel Request.
	'''

	if isinstance(expenses, str):
		expenses = json.loads(expenses)

	if not expenses:
		frappe.throw(_("Please provide at least one expense item."))

	expense_claim = frappe.new_doc("Expense Claim")
	expense_claim.travel_request = travel_request
	expense_claim.is_budgeted = is_budgeted
	expense_claim.is_budget_exceeded = is_budget_exceeded
	expense_claim.employee = employee
	expense_claim.approval_status = "Draft"
	expense_claim.posting_date = today()
	employee_doc = frappe.db.get_value("Employee", employee,["company","expense_approver"],as_dict=True)
	company = employee_doc.company

	expense_approver = employee_doc.expense_approver
	expense_claim.expense_approver = expense_approver


	default_payable_account = frappe.get_cached_value('Company', company, 'default_payable_account')
	if not default_payable_account:
		default_payable_account = frappe.db.get_value("Account", {
			"company": company,
			"account_type": "Payable",
			"is_group": 0
		}, "name")

	if not default_payable_account:
		frappe.throw(_("Please set a Default Payable Account in Company {0}").format(company))

	expense_claim.payable_account = default_payable_account

	for expense in expenses:
		amount = expense.get("amount")
		if amount in [None, ""]:
			frappe.throw(_("Expense Amount is required for all items."))

		expense_entry = {
			"amount": amount,
			"expense_date": expense.get("expense_date"),
			"expense_type": expense.get("expense_type"),
			"description": expense.get("description")
		}
		expense_claim.append("expenses", expense_entry)

	expense_claim.total_claimed_amount = sum((item.amount or 0) for item in expense_claim.expenses)
	expense_claim.save()
	assign_todo_for_expense_approver(expense_claim.name, travel_request, expense_approver)

	frappe.msgprint(
		_('Expense Claim Created: <a href="{0}">{1}</a>').format(get_url_to_form("Expense Claim", expense_claim.name), expense_claim.name),
		alert=True,indicator='green')

	return expense_claim.name


def assign_todo_for_expense_approver(expense_claim_name, travel_request, expense_approver):
	'''
	Create a ToDo for Accounts User(s) when a Expense claim
	is created and linked to the Employee Travel Request.
	'''
	if not expense_approver:
		return
	user_id = expense_approver  
	exists = frappe.db.exists(
		"ToDo",{ 
			"reference_type": "Expense Claim", 
			"reference_name": expense_claim_name, 
			"allocated_to": user_id 
		},
	)
	if not exists:
		description = (
			f"Expense Claim <b>{expense_claim_name}</b> has been created "
			f"for Employee Travel Request <b>{travel_request}</b>.<br>"
			"Please review and take necessary action."
		)
		add_assign({
			"assign_to": [user_id],
			"doctype": "Expense Claim",
			"name": expense_claim_name,
			"description": description,
		})


@frappe.whitelist()
def get_expense_claim_html(travel_id):
	"""
	Render HTML showing Expense Claims and their 'expenses'  for a given Travel Request.

	Args:
		travel_request_id (str): The name/ID of the Travel Request document.

	Returns:
		dict: A dictionary containing the rendered HTML.
	"""
	if not travel_id:
		frappe.throw(_("Travel Request ID is required."))

	expense_claims = frappe.get_all(
		"Expense Claim",
		filters={"travel_request": travel_id},
		fields=["name", "employee", "total_claimed_amount", "posting_date", "status"]
	)

	full_claims = []
	total_amount = 0
	total_sanctioned_amount = 0
	for claim in expense_claims:
		ec_doc = frappe.get_doc("Expense Claim", claim.name)
		expenses = sorted(
			ec_doc.expenses,
			key=lambda x: x.expense_date,
			reverse=True
		)
		for row in expenses:
			total_amount += row.amount or 0
			total_sanctioned_amount += row.sanctioned_amount or 0

		full_claims.append({
			"name": ec_doc.name,
			"employee": ec_doc.employee,
			"posting_date": ec_doc.posting_date,
			"status": ec_doc.status,
			"url": frappe.utils.get_url_to_form("Expense Claim", claim.name),
			"expenses": [
				{
					"expense_date": row.expense_date,
					"expense_type": row.expense_type,
					"default_account": row.default_account,
					"description": row.description,
					"amount": row.amount,
					"sanctioned_amount": row.sanctioned_amount,
				}
				for row in expenses
			]
		})

	html = frappe.render_template(
		"beams/doctype/employee_travel_request/expense_claim.html",
		{
			"expense_claims": full_claims,
			"total_amount": total_amount,
			"total_sanctioned_amount": total_sanctioned_amount
		}
	)

	return {"html": html}

@frappe.whitelist()
def get_permission_query_conditions(user):
	"""
	Returns SQL query conditions for controlling access to Employee Travel Requests.

	Rules:
	- "Admin" and "System Manager": full access.
	- "HOD": requests from employees in their department.
	- Employees: their own requests.
	- Others: no access.

	Args:
		user (str): User ID. Defaults to current session user.

	Returns:
		str: SQL conditions or None for unrestricted access.
	"""
	if not user:
		user = frappe.session.user

	user_roles = frappe.get_roles(user)

	if "Admin" in user_roles or "System Manager" in user_roles:
		return None

	conditions = []

	if "HOD" in user_roles:
		if frappe.db.exists("Employee",{"user_id":user}):
			department = frappe.db.get_value("Employee", {"user_id": user}, "department")
			if department:
				conditions.append(f"""
					EXISTS (
						SELECT 1 FROM `tabEmployee` e
						WHERE e.name = `tabEmployee Travel Request`.requested_by
						AND e.department = '{department}'
					)
				""")

	employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
	if employee_id:
		conditions.append(f"`tabEmployee Travel Request`.requested_by = '{employee_id}'")

	if not conditions:
		return "1=0"

	return " OR ".join(f"({cond.strip()})" for cond in conditions)

@frappe.whitelist()
def create_journal_entry_from_travel(employee, employee_travel_request, expenses, mode_of_payment, is_budgeted, is_budget_exceeded):
	"""
		Create a Journal Entry from Travel Request
	"""
	if isinstance(expenses, str):
		expenses = frappe.parse_json(expenses)

	if not isinstance(expenses, list):
		frappe.throw(_("Expenses must be a list of expense items."))

	company = frappe.defaults.get_user_default("Company")
	mop_account = frappe.db.get_value(
		"Mode of Payment Account",
		{
			"parent": mode_of_payment,
			"company": company
		},
		"default_account"
	)
	if not mop_account:
		frappe.throw(_(f"No default account found for Mode of Payment {mode_of_payment} for company {company}"))
	posting_date = nowdate()

	jv = frappe.new_doc("Journal Entry")
	jv.voucher_type = "Journal Entry"
	jv.posting_date = posting_date
	jv.company = company
	jv.user_remark = f"Journal Entry for Travel Request {employee_travel_request}"
	jv.employee = employee
	jv.employee_travel_request = employee_travel_request
	jv.is_budget_exceeded = is_budget_exceeded
	jv.is_budgeted = is_budgeted
	jv.docstatus = 0

	total_amount = 0

	for expense in expenses:
		expense_type = expense.get("expense_type")
		amount = expense.get("amount")
		expense_date = expense.get("expense_date")

		if not expense_type:
			frappe.throw(_("Expense Type is required for each expense item."))
		if not amount or not expense_date:
			frappe.throw(_("Amount and Expense Date are required for each expense item."))

		expense_claim = frappe.get_doc("Expense Claim Type", expense_type)
		debit_account = None
		for account_row in expense_claim.get("accounts", []):
			if account_row.default_account:
				debit_account = account_row.default_account
				break
		if not debit_account:
			frappe.throw(_(f"No default account found for Expense Claim Type {expense_type}"))


		jv.append("accounts", {
			"account": debit_account,
			"party_type": "Employee",
			"party": employee,
			"debit_in_account_currency": amount,
			"posting_date": posting_date
		})
		total_amount += amount

	jv.append("accounts", {
		"account": mop_account,
		"credit_in_account_currency": total_amount,
		"posting_date": posting_date
	})

	jv.insert()
	assign_todo_for_accounts(employee_travel_request, jv.name)
	return jv.name

def assign_todo_for_accounts(employee_travel_request, journal_entry_name):
	'''
	Create a ToDo for Accounts User(s) when a Journal Entry
	is created and linked to the Employee Travel Request.
	'''
	users = get_users_with_role("Accounts User")

	if users:
		for user in users:
			exists = frappe.db.exists(
				"ToDo", {
					"reference_type": "Journal Entry", 
					"reference_name": journal_entry_name, 
					"allocated_to": user 
			}
		)
			if not exists:
				description = (
					f"Journal Entry <b>{journal_entry_name}</b> has been created "
					f"for Employee Travel Request <b>{employee_travel_request}</b>.<br>"
					"Please review and take necessary action."
				)
				add_assign({
					"assign_to": [user],  
					"doctype": "Journal Entry",
					"name": journal_entry_name,
					"description": description
				})

@frappe.whitelist()
def create_batta_claim_from_etr(travel_request, is_budgeted, is_budget_exceeded):
	'''
	Create Batta Claim from Employee Travel Request.
	'''
	doc = frappe.get_doc("Employee Travel Request", travel_request)
	employee = doc.requested_by

	if not employee:
		frappe.throw("No Employee linked to this Travel Request.")

	existing_bc_name = frappe.db.exists("Batta Claim", {"travel_request": doc.name})
	if existing_bc_name:
		return {"status": "exists", "name": existing_bc_name}

	bc = frappe.new_doc("Batta Claim")
	bc.travel_request = doc.name
	bc.employee = employee
	bc.is_budgeted = is_budgeted
	bc.is_budget_exceeded = is_budget_exceeded
	bc.origin = doc.source
	bc.destination = doc.destination
	bc.purpose= doc.travel_type
	bc.is_travelling_outside_kerala = 0 if doc.inside_kerala else 1

	if doc.get("mode_of_travel"):
		bc.append("mode_of_travelling", {
			"mode_of_travel": doc.mode_of_travel
		})

	if hasattr(bc, 'work_detail'):
		work_detail_row = {
			"from_date_and_time": doc.start_date,
			"to_date_and_time": doc.end_date
		}

		start = get_datetime(doc.start_date)
		end = get_datetime(doc.end_date)

		diff_hours = (end - start).total_seconds() / 3600
		work_detail_row["total_hours"] = diff_hours if diff_hours > 0 else 0

		if doc.get("source"):
			work_detail_row["origin"] = doc.source
		if doc.get("destination"):
			work_detail_row["destination"] = doc.destination

		bc.append("work_detail", work_detail_row)

		bc.insert(ignore_permissions=True)

	return {"status": "new", "name": bc.name}

