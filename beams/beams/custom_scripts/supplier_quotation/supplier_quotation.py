import frappe
from frappe.model.mapper import get_mapped_doc



@frappe.whitelist()
def make_purchase_order_from_supplier_quotation(source_name, target_doc=None):
	'''Map Supplier Quotation to Purchase Order including both Items tables.
		Filters out items without Qty and Rate.'''
	def postprocess(source_doc, target_doc,source_parent):
		target_doc.items = []
		for row in source_doc.get("items", []):
			if row.qty and row.rate:
				target_doc.append("items", {
					"item_code": row.item_code,
					"item_name": row.item_name,
					"qty": row.qty,
					"rate": row.rate,
					"uom": row.uom,
					"stock_uom": row.stock_uom,               
					"conversion_factor": row.conversion_factor
				})
		for row in source_doc.get("suggested_items_by_supplier", []):
			if row.quantity and row.rate:
				target_doc.append("items", {
					"item_code": row.item_code,
					"item_name": row.product_name,
					"qty": row.quantity,
					"rate": row.rate,
					"uom": row.uom,
					"stock_uom": row.uom,               
					"conversion_factor": 1
				})
	target_doc = get_mapped_doc(
		"Supplier Quotation",
		source_name,
		{
			"Supplier Quotation": {
				"doctype": "Purchase Order",
				"field_map": {
					"supplier": "supplier",
				},
				"postprocess": postprocess
			}
		},
		target_doc
	)

	return target_doc
