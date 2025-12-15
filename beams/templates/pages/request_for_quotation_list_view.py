import frappe
from frappe import _
from frappe.utils import formatdate
from erpnext.controllers.website_list_for_contact import get_customers_suppliers


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True

	# Get Supplier for current user
	supplier = get_supplier()
	if not supplier:
		frappe.throw(_("No Supplier linked to this user"), frappe.PermissionError)


	# Ensure supplier has permission to see RFQs
	if not check_supplier_has_any_rfq(supplier):
		context.rfq_list = []
		return context

	context.rfq_list = get_supplier_rfq_list(supplier)

	context.title = _("Request for Quotation")

	return context


def get_supplier():
	"""Return supplier linked to current user using ERPNext mapping util"""
	customers, suppliers = get_customers_suppliers(
		"Request for Quotation Supplier", frappe.session.user
	)
	return suppliers[0] if suppliers else None


def check_supplier_has_any_rfq(supplier):
	"""Check if supplier has at least one assigned RFQ"""
	rfqs = frappe.db.get_all(
		"Request for Quotation Supplier",
		filters={"supplier": supplier},
		limit=1
	)
	return bool(rfqs)


def get_supplier_rfq_list(supplier):
	"""
	Return list of RFQs assigned to this supplier with item count.
	Matches your Jinja template structure exactly.
	"""

	rfqs = frappe.db.sql(
		"""
		SELECT
			r.name,
			r.transaction_date,
			r.status,
			r.schedule_date AS due_date,
			COUNT(i.name) AS item_count
		FROM `tabRequest for Quotation` r
		LEFT JOIN `tabRequest for Quotation Item` i ON i.parent = r.name
		WHERE r.name IN (
			SELECT parent
			FROM `tabRequest for Quotation Supplier`
			WHERE supplier = %(supplier)s
		)
		GROUP BY r.name
		ORDER BY r.creation DESC
		""",
		{"supplier": supplier},
		as_dict=True,
	)

	for row in rfqs:
		row.transaction_date = formatdate(row.transaction_date)
		if row.due_date:
			row.due_date = formatdate(row.due_date)

	return rfqs
