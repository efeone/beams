
import frappe
from frappe import _
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role
from frappe.utils import getdate


def validate_reason_for_rejection(doc,method):
	'''
		Validate that "Reason for Rejection" is filled if the status is "Rejected"
	'''
	rejection_states = [
		"Rejected",
		"Rejected By Finance",
		"Rejected by CEO"
	]

	if doc.workflow_state in rejection_states and not doc.reason_for_rejection:
		frappe.throw("Please provide a Reason for Rejection before rejecting this request.")

@frappe.whitelist()
def create_todo_on_finance_verification(doc, method):
	"""
		Create a ToDo for the CEO when a Purchase Order is either approved or rejected by Finance.
	"""
	ceo_users = get_users_with_role("CEO")

	if not ceo_users:
		return

	if doc.workflow_state == "Approved by Finance":
		description = f"Approved by Finance: Purchase Order-{doc.supplier}.<br>Please proceed with the next step."
	elif doc.workflow_state == "Rejected By Finance":
		description = f"Rejected by Finance: Purchase Order-{doc.supplier}.<br>Please review and revise, or proceed with their feedback."
	else:
		return

	if not frappe.db.exists('ToDo', {
		'reference_name': doc.name,
		'reference_type': 'Purchase Order',
		'description': description
	}):
		add_assign({
			"assign_to": ceo_users,
			"doctype": "Purchase Order",
			"name": doc.name,
			"description": description
		})

@frappe.whitelist()
def fetch_department_from_cost_center(doc, method):
	"""
		Automatically fetch the department based on the selected cost center
		in both Purchase Order and Material Request.
	"""
	for row in doc.get("items"):
		if row.cost_center:
			department = frappe.get_value('Department', {'cost_center': row.cost_center}, 'name')
			if department:
				row.department = department
			else:
				frappe.msgprint(_("No department found for the selected Cost Center {0}.").format(row.cost_center))

@frappe.whitelist()
def update_equipment_quantities(doc, method):
	"""
	Update the 'acquired_quantity' field in the 'Required Acquiral Items' child table and project
	of the linked Equipment Acquiral Request when the Purchase Order is submitted.
	"""
	old_doc = doc.get_doc_before_save()
	if old_doc and old_doc.per_received != 100:
		if doc.workflow_state == "Approved":
			if doc.items:
				for item in doc.items:
					if hasattr(item, 'reference_document') and item.reference_document:
						# Update acquired_qty in Required Acquiral Items Detail
						ea_a_qty = frappe.db.get_value("Required Acquiral Items Detail", item.reference_document, "acquired_qty")
						frappe.db.set_value(
							"Required Acquiral Items Detail",
							item.reference_document,
							"acquired_qty",
							(ea_a_qty + item.qty)
						)
						equipment_a_request = frappe.db.get_value("Required Acquiral Items Detail", item.reference_document, "parent")
						ea_item = frappe.db.get_value("Required Acquiral Items Detail", item.reference_document, "item")

						if equipment_a_request:
							equipment_request = frappe.db.get_value("Equipment Acquiral Request", equipment_a_request, "equipment_request")
							if equipment_request:
								er_doc = frappe.get_doc("Equipment Request", equipment_request)
								for e_item in er_doc.required_equipments:
									if e_item.required_item == ea_item:
										e_item.acquired_quantity = (e_item.acquired_quantity + item.qty)
								er_doc.save()

								project = frappe.db.get_value("Equipment Request", equipment_request, "project")
								if project:
									project_doc = frappe.get_doc("Project", project)
									item_found = False
									for p_item in project_doc.allocated_item_details:
										if p_item.required_item == ea_item:
											p_item.acquired_quantity = (p_item.acquired_quantity or 0) + item.qty
											item_found = True
											break

									if not item_found:
										required_qty = 0
										for e_item in er_doc.required_equipments:
											if e_item.required_item == ea_item:
												required_qty = e_item.required_quantity
												break

										project_doc.append("allocated_item_details", {
											"required_item": ea_item,
											"required_quantity": required_qty,
											"acquired_quantity": item.qty
										})

									project_doc.save()

def validate(doc, method=None):
	'''
	This function validates the expenses for each item in the document against the defined budget.
	'''
	for item in doc.items:
		if item.cost_center:

			budget = frappe.get_value(
				'Budget',
				{'cost_center': item.cost_center, 'fiscal_year': doc.fiscal_year},
				'total_budget'
			)
			actual_expense = frappe.db.sql("""
				SELECT SUM(credit)
				FROM `tabGL Entry`
				WHERE cost_center = %s
				AND account = %s
				AND fiscal_year = %s
			""", (item.cost_center, item.expense_account, doc.fiscal_year))

			total_expense = actual_expense[0][0] or 0
			total_expense += item.amount

			if budget and total_expense > budget:
				doc.is_budget_exceed = 1
				frappe.msgprint(
					_("The budget for Cost Center {0} has been exceeded.").format(item.cost_center)
				)

def validate_budget(doc, method=None):
	"""
		Validate the expenses in the document against the defined budget for each item.
	"""

	from beams.beams.overrides.budget import validate_expense_against_budget

	if doc.name:
		for data in doc.get("items"):

			args = data.as_dict()

			args.update({
				"object": doc,
				"doctype": doc.doctype,
				"parent": doc.name,
				"company": doc.company,
				"posting_date": (
					doc.schedule_date
					if doc.doctype == "Material Request"
					else doc.transaction_date
				),
			})

			validate_expense_against_budget(args)			

def set_is_budgeted(doc, method=None):
	"""
		Set the 'is_budgeted' and 'is_budget_exceeded' fields based on whether the expenses in the document are budgeted and if any budget is exceeded.
	"""

	is_budgeted = 0
	is_budget_exceeded = 0
	transaction_date = (
		doc.get("posting_date")
		or doc.get("transaction_date")
	)

	if not transaction_date:
		return

	transaction_date = getdate(transaction_date)
	month = transaction_date.strftime("%B").lower()
	items = doc.get("items") or doc.get("accounts") or doc.get("expenses") or []

	for item in items:

		cost_center = item.get("cost_center")
		project = item.get("project")
		expense_account = (
			item.get("expense_account")
			or item.get("account")
		)
		if doc.doctype == "Expense Claim":
			expense_type = item.get("expense_type")

			if expense_type:
				expense_account = frappe.db.get_value(
					"Expense Claim Account",
					{
						"parent": expense_type,
						"company": doc.company
					},
					"default_account"
				)

		item_amount = (
			item.get("base_amount")
			or item.get("debit")
			or item.get("amount")
			or 0
		)

		if not expense_account:
			continue

		budgets = frappe.get_all(
			"Budget",
			filters={"docstatus": 1},
			fields=[
				"name",
				"fiscal_year",
				"cost_center",
				"project",
				"action_if_annual_budget_exceeded",
				"action_if_accumulated_monthly_budget_exceeded"
			]
		)

		for budget in budgets:
			if budget.cost_center and budget.cost_center != cost_center:
				continue
			if budget.project and budget.project != project:
				continue

			fy = frappe.get_doc("Fiscal Year", budget.fiscal_year)
			if not (fy.year_start_date <= transaction_date <= fy.year_end_date):
				continue
			budget_account = frappe.db.get_value(
				"Budget Account",
				{
					"parent": budget.name,
					"account": expense_account
				},
				[
					"budget_amount",
					month
				],
				as_dict=1
			)

			if not budget_account:
				continue

			is_budgeted = 1

			annual_budget = budget_account.budget_amount or 0
			monthly_budget = budget_account.get(month) or 0
			actual_expense = frappe.db.sql("""
				SELECT COALESCE(SUM(debit) - SUM(credit), 0)
				FROM `tabGL Entry`
				WHERE account=%s
				AND cost_center=%s
				AND posting_date BETWEEN %s AND %s
				AND docstatus=1
			""", (
				expense_account,
				cost_center,
				fy.year_start_date,
				fy.year_end_date
			))[0][0] or 0

			total_annual_expense = actual_expense + item_amount

			if annual_budget and total_annual_expense > annual_budget:
				if budget.action_if_annual_budget_exceeded in ["Stop", "Warn"]:
					is_budget_exceeded = 1
			monthly_expense = frappe.db.sql("""
				SELECT COALESCE(SUM(debit) - SUM(credit),0)
				FROM `tabGL Entry`
				WHERE account=%s
				AND cost_center=%s
				AND MONTH(posting_date)=MONTH(%s)
				AND YEAR(posting_date)=YEAR(%s)
				AND docstatus=1
			""", (
				expense_account,
				cost_center,
				transaction_date,
				transaction_date
			))[0][0] or 0

			total_monthly_expense = monthly_expense + item_amount

			if monthly_budget and total_monthly_expense > monthly_budget:
				if budget.action_if_accumulated_monthly_budget_exceeded in ["Stop", "Warn"]:
					is_budget_exceeded = 1

			break

		if is_budgeted:
			break

	doc.is_budgeted = is_budgeted
	doc.is_budget_exceeded = is_budget_exceeded