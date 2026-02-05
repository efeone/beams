
import frappe
from frappe import _
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role


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
