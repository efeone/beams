import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt


@frappe.whitelist()
def make_purchase_order_from_supplier_quotation(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

	def postprocess(source_doc, target_doc, source_parent):
		for row in source_doc.get("suggested_items_by_supplier", []):
			if row.quantity and row.rate:
				target_doc.append("items", {
					"item_code": row.item_code,
					"item_name": row.product_name,
					"qty": row.quantity,
					"rate": row.rate,
					"uom": row.uom,
					"stock_uom": row.uom,
					"conversion_factor": 1,
					"supplier_quotation": source_doc.name,
				})

	doclist = get_mapped_doc(
		"Supplier Quotation",
		source_name,
		{
			"Supplier Quotation": {
				"doctype": "Purchase Order",
				"validation": {
					"docstatus": ["=", 1],
				},
				"postprocess": postprocess
			},
			"Supplier Quotation Item": {
				"doctype": "Purchase Order Item",
				"condition": lambda doc: flt(doc.qty) > 0,
				"field_map": [
					["name", "supplier_quotation_item"],
					["parent", "supplier_quotation"],
					["material_request", "material_request"],
					["material_request_item", "material_request_item"],
					["sales_order", "sales_order"],
				],
				"postprocess": update_item,
			},
			"Purchase Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges",
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist

def clear_rate_if_no_rate_provided(doc, method):
	"''Clear rate and amount for items where no_rate_provided is set.'''"
	for item in doc.items:
		if item.no_rate_provided:
			item.rate = 0
			item.amount = 0
