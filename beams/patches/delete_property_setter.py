import frappe

def execute():
	filters_list = [
		{
			"doctype_or_field": "DocField",
			"doc_type": "Employee Feedback Rating",
			"field_name": "Rating",
			"property": "read_only",
			"property_type": "Check",
			"value": "1"
		},
		{
			"doctype_or_field": "DocField",
			"doc_type": "Employee Advance",
			"field_name": "purpose",
			"property": "hidden",
			"property_type": "Small Text",
			"value":1
		},
	]

	for filters in filters_list:
		property_setter_name = frappe.db.exists("Property Setter", filters)
		if property_setter_name:
			frappe.db.delete("Property Setter", {"name": property_setter_name})
	frappe.db.commit()
