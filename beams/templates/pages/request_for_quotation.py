import frappe
from frappe import _
from frappe.utils import formatdate

from erpnext.controllers.website_list_for_contact import get_customers_suppliers
import json


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True

	rfq = frappe.form_dict.rfq

	# Get supplier linked to current user
	supplier = get_supplier()
	if not supplier:
		frappe.throw(_("No Supplier linked to this user"), frappe.PermissionError)


	# Load RFQ doc
	context.doc = frappe.get_doc("Request for Quotation", rfq)
	context.doc.supplier = supplier

	# Ensure supplier has access
	unauthorized_user(supplier)

	# Linked quotations
	context.doc.rfq_links = get_link_quotation(supplier, context.doc.name)

	# Supplier details
	update_supplier_details(context)

	# Page title
	context["title"] = context.doc.name
	return context


def get_supplier():
	"""Return supplier linked to current user"""
	customers, suppliers = get_customers_suppliers(
		"Request for Quotation Supplier", frappe.session.user
	)
	return suppliers[0] if suppliers else None



def check_supplier_has_docname_access(supplier):
	"""Ensure supplier has access to this RFQ"""
	rfqs = frappe.db.get_all(
		"Request for Quotation Supplier",
		filters={"supplier": supplier},
		fields=["parent"],
		limit=1
	)
	return bool(rfqs)


def unauthorized_user(supplier):
	if not check_supplier_has_docname_access(supplier):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)


def update_supplier_details(context):
	"""Attach supplier-related details to context.doc"""
	supplier_doc = frappe.get_doc("Supplier", context.doc.supplier)
	company_currency = frappe.get_cached_value("Company", context.doc.company, "default_currency")

	context.doc.currency = supplier_doc.default_currency or company_currency
	context.doc.currency_symbol = frappe.db.get_value(
		"Currency", context.doc.currency, "symbol", cache=True
	)
	context.doc.number_format = frappe.db.get_value(
		"Currency", context.doc.currency, "number_format", cache=True
	)
	context.doc.buying_price_list = supplier_doc.default_price_list or ""


def get_link_quotation(supplier, rfq):
	"""Get supplier quotations linked to this RFQ"""
	if not supplier:
		return []

	quotation = frappe.db.sql(
		""" select distinct `tabSupplier Quotation Item`.parent as name,
				   `tabSupplier Quotation`.status,
				   `tabSupplier Quotation`.transaction_date
			from `tabSupplier Quotation Item`
			inner join `tabSupplier Quotation`
				on `tabSupplier Quotation Item`.parent = `tabSupplier Quotation`.name
			where `tabSupplier Quotation`.docstatus < 2
			  and `tabSupplier Quotation Item`.request_for_quotation = %(name)s
			  and `tabSupplier Quotation`.supplier = %(supplier)s
			order by `tabSupplier Quotation`.creation desc
		""",
		{"name": rfq, "supplier": supplier},
		as_dict=1,
	)

	for data in quotation:
		data.transaction_date = formatdate(data.transaction_date)

	return quotation


@frappe.whitelist()
def save_supplier_quotation(data):
	"""Save Supplier Quotation from supplier portal"""

	data = json.loads(data)
 
	frappe.log_error("submit_supplier_quotation", data)
	

	supplier = data.get("supplier")
	rfq = data.get("rfq")
	items = data.get("items", [])
	suggested_items = data.get("suggested_items", [])
	notes = data.get("notes")

	if not supplier or not rfq:
		frappe.throw(_("Missing required data (supplier or rfq)"))

	quotation = frappe.new_doc("Supplier Quotation")
	quotation.supplier = supplier
	quotation.transaction_date = frappe.utils.nowdate()
	quotation.request_for_quotation = rfq
	quotation.notes = notes

	# Process original RFQ items
	for item in items:
		full_description = ""
		
		if item.get("brand"):
			full_description += f"Brand: {item['brand']}\n"
		if item.get("model"):
			full_description += f"Model: {item['model']}\n"
		if item.get("warranty"):
			full_description += f"Warranty: {item['warranty']}\n"
		if item.get("lead_time"):
			full_description += f"Lead Time: {item['lead_time']}\n"
		if item.get("item_description"):
			full_description += f"Details: {item['item_description']}\n"

		# Convert rate properly
		rate = float(item.get("rate") or 0)
		no_rate_flag = 1 if rate <= 0 else 0

		# If supplier didn't give rate → qty becomes 0
		qty = 0 if rate == 0 else item.get("qty")

		quotation.append("items", {
			"item_code": item.get("item_code"),
			"item_name": item.get("item_name"),
			"item_description": full_description.strip(),
			"qty": qty,
			"uom": item.get("uom"),
			"rate": rate,
			"request_for_quotation": rfq,
			"no_rate_provided": no_rate_flag,
		})


	# Process suggested items by supplier
	for suggested_item in suggested_items:
		quotation.append("suggested_items_by_supplier", {
			"product_name": suggested_item.get("product_name"),
			"quantity": suggested_item.get("quantity"),
			"rate": suggested_item.get("rate"),
			"uom": suggested_item.get("uom"),
			"amount": suggested_item.get("amount"),
			"product_description": suggested_item.get("product_description"),
			"item_description": suggested_item.get("item_description")
		})

	quotation.insert(ignore_permissions=True)

	total_original = len(items)
	total_suggested = len(suggested_items)
	
	return {
		"message": _("Quotation submitted successfully with {0} original items and {1} suggested items").format(total_original, total_suggested), 
		"name": quotation.name
	}
