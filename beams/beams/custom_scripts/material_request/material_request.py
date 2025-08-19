import frappe
import json
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc
from frappe.desk.form.assign_to import add as add_assign


@frappe.whitelist()
def notify_stock_managers(doc=None, method=None):
	"""
	Notifies all users with 'Stock Manager' role via email after a Material Request is created.
	Can be called from hooks or API.
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("Material Request", doc)

	# Fetch users with "Stock Manager" role and their email addresses
	recipients = [
		user.email for user in frappe.get_all(
			"User",
			filters={
				"enabled": 1,
				"user_type": "System User"
			},
			fields=["name", "email"]
		) if any(role in frappe.get_roles(user.name) for role in ["Stock Manager", "Admin"])
	]

	if not recipients:
		return

	subject = f"📦 New Material Request: {doc.name}"
	message = frappe.render_template(
		"""
		<p>Hello,</p>
		<p>A new <strong>Material Request</strong> has been created:</p>
		<ul>
			<li><strong>Name:</strong> {{ doc.name }}</li>
			<li><strong>Type:</strong> {{ doc.material_request_type }}</li>
			<li><strong>Date:</strong> {{ doc.transaction_date }}</li>
			<li><strong>Requested By:</strong> {{ doc.owner }}</li>
		</ul>
		<p>Please log in to review it.</p>
		""",
		{"doc": doc}
	)

	frappe.sendmail(
		recipients=recipients,
		subject=subject,
		message=message,
		delayed=False,
		reference_doctype="Material Request",
		reference_name=doc.name
	)

@frappe.whitelist()
def create_stock_entry_from_mr(material_request, source_warehouse, items):
	"""
		Create and submit a Stock Entry (Material Issue) from a Material Request
	"""
	if isinstance(items, str):
		items = json.loads(items or "[]")

	if not items:
		frappe.throw("No items provided to create Stock Entry")

	stock_entry = frappe.get_doc({
		"doctype": "Stock Entry",
		"stock_entry_type": "Material Issue",
		"material_request": material_request,
		"from_warehouse": source_warehouse,
		"items": []
	})

	for row in items:
		item_code = row.get("item_code")
		qty = flt(row.get("qty"))
		uom = row.get("uom")

		if not (item_code and qty > 0):
			continue

		if frappe.get_value("Item", item_code, "is_stock_item"):
			stock_entry.append("items", {
				"item_code": item_code,
				"qty": qty,
				"s_warehouse": source_warehouse,
				"uom": uom
			})

	stock_entry.insert(ignore_permissions=True)
	stock_entry.submit()

	return stock_entry.name

@frappe.whitelist()
def map_asset_movement_from_mr(source_name, assigned_to=None, items=None, purpose="Issue", target_doc=None):
	"""
		Create and submit an Asset Movement document from a Material Request.
	"""
	if isinstance(items, str):
		items = json.loads(items or "[]")

	employee_id = frappe.get_value("Employee", {"user_id": assigned_to})
	if not employee_id:
		frappe.throw(f"No Employee linked to User '{assigned_to}'")

	def postprocess(source, target):
		target.to_employee = employee_id
		target.reference_doctype = "Material Request"
		target.reference_name = source.name
		target.purpose = purpose or "Issue"

		for row in (items or []):
			item_code = row.get("item")
			asset_name = row.get("asset")
			qty = frappe.utils.flt(row.get("qty"))

			if not (item_code and asset_name and qty > 0):
				continue

			target.append("assets", {
				"asset": asset_name,
				"source_location": frappe.get_value("Asset", asset_name, "location"),
				"to_employee": employee_id,
				"reference_name": row.get("name")
			})

	asset_movement = get_mapped_doc(
		"Material Request",
		source_name,
		{"Material Request": {"doctype": "Asset Movement"}},
		target_doc,
		postprocess
	)

	asset_movement.insert(ignore_permissions=True)
	asset_movement.submit()

	return asset_movement.name

def create_todo_for_hod(doc, method):
	"""
	Creates a ToDo for the Head of Department
	only when transitioning from 'Draft' → 'Informed HOD'
	"""
	old_doc = doc.get_doc_before_save()

	# Run only if workflow_state changed from Draft to Informed HOD
	if not old_doc or not (
		old_doc.workflow_state == "Draft" and doc.workflow_state == "Informed HOD"
	):
		return

	# Ensure employee exists for the doc.owner
	if not frappe.db.exists("Employee", {"user_id": doc.owner}):
		return

	employee_id, department = frappe.db.get_value(
		"Employee",
		{"user_id": doc.owner},
		["name", "department"]
	)

	if not department or not frappe.db.exists("Department", department):
		return

	# Get HOD of that department
	hod_emp_id = frappe.db.get_value("Department", department, "head_of_department")
	if not hod_emp_id or not frappe.db.exists("Employee", hod_emp_id):
		return

	hod_user = frappe.db.get_value("Employee", hod_emp_id, "user_id")
	if not hod_user:
		return

	# Assign ToDo to HOD
	add_assign({
		"doctype": doc.doctype,
		"name": doc.name,
		"assign_to": [hod_user],
		"assigned_by": frappe.session.user,
		"priority": "Medium",
		"description": f"Please review Material Request {doc.name}"
	})
