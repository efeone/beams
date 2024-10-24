
import frappe
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role

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

def create_todo_on_purchase_order_creation(doc, method):
	"""
		Create a ToDo for  Accounts User when a new Purchase Order is created.
	"""
	users = get_users_with_role("Accounts User")

	if users:
		description = f"New Purchase Order Created: {doc.supplier}.<br>Please review and update details or take necessary actions."
		add_assign({
			"assign_to": users,
			"doctype": "Purchase Order",
			"name": doc.name,
			"description": description
		})

def validate(self):
	'''
		This function validates the expenses for each item in the document against the defined budget.
	'''
	for item in self.items:
		if item.cost_center:
			budget = frappe.get_value('Budget', {'cost_center': item.cost_center, 'fiscal_year': self.fiscal_year}, 'total_budget')

			# Get the actual expenses from GL Entry
			actual_expense = frappe.db.sql("""
				SELECT SUM(credit)
				FROM `tabGL Entry`
				WHERE cost_center = %s
				AND account = %s
				AND fiscal_year = %s
			""", (item.cost_center, item.expense_account, self.fiscal_year))

			# Calculate the total expense including the current Purchase Order amount
			total_expense = actual_expense[0][0] or 0
			total_expense += item.amount

			if total_expense > budget:
				self.is_budget_exceed = 1  # Automatically check the checkbox
				frappe.msgprint(_("The budget for Cost Center {0} has been exceeded.").format(item.cost_center))

def validate_budget(self, method=None):
	'''
		Validating Budget for Purchase order and material request
	'''
	from beams.beams.overrides.budget import validate_expense_against_budget
	if self.name:
		for data in self.get("items"):
			args = data.as_dict()
			args.update(
				{
					"object": self,
					"doctype": self.doctype,
					"company": self.company,
					"posting_date": (
						self.schedule_date
						if self.doctype == "Material Request"
						else self.transaction_date
					),
				}
			)

			validate_expense_against_budget(args)

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
