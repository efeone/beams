import frappe

@frappe.whitelist()
def get_default_account_of_cost_head(cost_head, company):
	"""
		Method to get default account of cost head
	"""
	return frappe.db.get_value("Accounts", {"parent": cost_head, "company": company}, "default_account")
