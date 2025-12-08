import frappe

def update_ticket_type(doc, method):
	"""
		Create or update HD Ticket ticket_type Property Setter from HD Settings.
	"""

	default_ticket_type = doc.default_ticket_type

	if default_ticket_type:
		ps = frappe.db.exists("Property Setter", {
			"doctype_or_field": "DocField",
			"doc_type": "HD Ticket",
			"field_name": "ticket_type",
			"property": "default"
		})

		if ps:
			# Update existing Property Setter
			prop_setter = frappe.get_doc("Property Setter", ps)
			prop_setter.value = default_ticket_type
			prop_setter.save()
		else:
			# Create new Property Setter
			prop_setter = frappe.get_doc({
				"doctype": "Property Setter",
				"doctype_or_field": "DocField",
				"doc_type": "HD Ticket",
				"field_name": "ticket_type",
				"property": "default",
				"property_type": "Data",
				"value": default_ticket_type
			})
			prop_setter.insert()
	else:
		# Remove existing Property Setter if default_ticket_type is not set
		ps = frappe.db.exists("Property Setter", {
			"doctype_or_field": "DocField",
			"doc_type": "HD Ticket",
			"field_name": "ticket_type",
			"property": "default"
		})

		if ps:
			frappe.delete_doc("Property Setter", ps)
