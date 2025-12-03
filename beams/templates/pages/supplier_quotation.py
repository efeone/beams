import frappe
from frappe import _
from frappe.utils import formatdate, fmt_money

def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True

	sq_name = frappe.form_dict.name
	
	if not sq_name:
		frappe.throw(_("Supplier Quotation name is required"), frappe.ValidationError)

	# Get supplier linked to current user
	supplier = get_supplier()
	if not supplier:
		frappe.throw(_("No Supplier linked to this user"), frappe.PermissionError)

	context.doc = frappe.get_doc("Supplier Quotation", sq_name)

	# Ensure supplier has access
	if context.doc.supplier != supplier:
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

	# Format dates and currency
	context.doc.formatted_date = formatdate(context.doc.transaction_date)
	context.doc.formatted_valid_till = formatdate(context.doc.valid_till) if context.doc.valid_till else ""

	# Get currency symbol
	context.doc.currency_symbol = frappe.db.get_value(
		"Currency", context.doc.currency, "symbol", cache=True
	) if context.doc.currency else "₹"

	# Calculate totals for items with rates
	calculate_totals(context.doc)

	# Page title
	context["title"] = f"Supplier Quotation - {context.doc.name}"
	
	return context


def get_supplier():
	"""Return supplier linked to current user"""
	from erpnext.controllers.website_list_for_contact import get_customers_suppliers
	customers, suppliers = get_customers_suppliers(
		"Supplier Quotation", frappe.session.user
	)
	return suppliers[0] if suppliers else None


def calculate_totals(doc):
	"""Calculate totals for items with rates provided"""
	doc.items_with_rate = []
	doc.items_without_rate = []
	doc.total_items_count = len(doc.items)
	doc.items_quoted_count = 0
	
	for item in doc.items:
		if item.rate and item.rate > 0:
			doc.items_with_rate.append(item)
			doc.items_quoted_count += 1
		else:
			doc.items_without_rate.append(item)
	
	doc.items_not_quoted_count = doc.total_items_count - doc.items_quoted_count


@frappe.whitelist()
def update_supplier_quotation(data):
	"""Update Supplier Quotation from supplier portal"""
	import json
	
	data = json.loads(data)
	doc_name = data.get("name")
	
	if not doc_name:
		frappe.throw(_("Supplier Quotation name is required"))
	
	supplier = get_supplier()
	if not supplier:
		frappe.throw(_("No Supplier linked to this user"), frappe.PermissionError)
	
	doc = frappe.get_doc("Supplier Quotation", doc_name)
	
	if doc.supplier != supplier:
		frappe.throw(_("Not Permitted"), frappe.PermissionError)
	
	# Only allow editing draft documents
	if doc.docstatus != 0:
		frappe.throw(_("Only draft documents can be edited."))
	
	# Update quoted items (qty and rate)
	for item_data in data.get("items", []):
		item_name = item_data.get("name")
		if item_name:
			for item in doc.items:
				if item.name == item_name:
					item.no_rate_provided = 0
					item.qty = item_data.get("qty", item.qty)
					item.rate = item_data.get("rate", item.rate)
					break
	
	# Update suggested items
	doc.suggested_items_by_supplier = []
	
	# Add updated/new suggested items
	for suggested_data in data.get("suggested_items", []):
		doc.append("suggested_items_by_supplier", {
			"product_name": suggested_data.get("product_name"),
			"product_description": suggested_data.get("product_description"),
			"quantity": suggested_data.get("quantity"),
			"uom": suggested_data.get("uom"),
			"rate": suggested_data.get("rate"),
			"amount": suggested_data.get("quantity", 0) * suggested_data.get("rate", 0)
		})
	
	doc.notes = data.get("notes", "")

	doc.save(ignore_permissions=True)
	
	return {
		"message": _("Quotation updated successfully"),
		"name": doc.name
	}
