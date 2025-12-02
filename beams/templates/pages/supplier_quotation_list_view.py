import frappe
from frappe import _
from frappe.utils import formatdate
from erpnext.controllers.website_list_for_contact import get_customers_suppliers


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True

	# Get Supplier for current logged-in user
	supplier = get_supplier()
	if not supplier:
		frappe.throw(_("No Supplier linked to this user"), frappe.PermissionError)

	# Ensure supplier has any Supplier Quotation
	if not check_supplier_has_any_sq(supplier):
		context.supplier_quotation_list = []
		return context

	# Fetch list for template
	context.supplier_quotation_list = get_supplier_quotation_list(supplier)

	context.title = _("Supplier Quotations")

	return context


def get_supplier():
	"""Return supplier linked to current user"""
	customers, suppliers = get_customers_suppliers(
		"Supplier Quotation", frappe.session.user
	)
	return suppliers[0] if suppliers else None


def check_supplier_has_any_sq(supplier):
	"""Check if supplier has at least one Supplier Quotation"""

	sq = frappe.db.get_all(
		"Supplier Quotation",
		filters={"supplier": supplier},
		limit=1
	)
	return bool(sq)


def get_supplier_quotation_list(supplier):
	"""
	Return Supplier Quotation list for this supplier.
	"""

	sq_list = frappe.db.sql(
		"""
		SELECT
			sq.name,
			sq.title,
			sq.status,
			sq.transaction_date,
			sq.valid_till,
			sq.grand_total,
			sq.net_total,
			COUNT(it.name) AS item_count
		FROM `tabSupplier Quotation` sq
		LEFT JOIN `tabSupplier Quotation Item` it
			ON it.parent = sq.name
		WHERE sq.supplier = %(supplier)s
		GROUP BY sq.name
		ORDER BY sq.creation DESC
		""",
		{"supplier": supplier},
		as_dict=True,
	)

	for row in sq_list:
		if row.transaction_date:
			row.transaction_date = formatdate(row.transaction_date)

		if row.valid_till:
			row.valid_till = formatdate(row.valid_till)

	return sq_list
