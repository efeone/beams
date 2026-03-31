import frappe
from frappe import _
from frappe.utils import flt, getdate


def on_submit(doc, method=None):
	"""When a Journal Entry linked to a Bureau Trip Sheet is submitted (docstatus=1), add it to the BTS settlement table."""
	if not getattr(doc, "bureau_trip_sheet", None):
		return
	bts_name = doc.bureau_trip_sheet
	if not frappe.db.exists("Bureau Trip Sheet", bts_name):
		return
	# Avoid duplicate row if already in table
	existing = frappe.db.get_all(
		"Bureau Trip Sheet Journal Entry",
		filters={"parent": bts_name, "parenttype": "Bureau Trip Sheet", "journal_entry": doc.name},
		limit=1,
	)
	if existing:
		return
	# Settlement amount = total debit (or credit) in the JE
	amount = sum(flt(acc.get("debit_in_account_currency") or 0) for acc in (doc.accounts or []))
	if amount <= 0:
		amount = sum(flt(acc.get("credit_in_account_currency") or 0) for acc in (doc.accounts or []))
	bts = frappe.get_doc("Bureau Trip Sheet", bts_name)
	bts.append("settlement_journal_entries", {
		"journal_entry": doc.name,
		"posting_date": getdate(doc.posting_date),
		"amount": amount,
	})
	bts.flags.ignore_validate_update_after_submit = True
	bts.save(ignore_permissions=True)


def on_cancel(doc, method):
	# Remove this JE from Bureau Trip Sheet settlement_journal_entries if linked
	bts_name = getattr(doc, "bureau_trip_sheet", None)
	if bts_name and frappe.db.exists("Bureau Trip Sheet", bts_name):
		child = frappe.db.get_value(
			"Bureau Trip Sheet Journal Entry",
			{"parent": bts_name, "parenttype": "Bureau Trip Sheet", "journal_entry": doc.name},
			"name",
		)
		if child:
			bts = frappe.get_doc("Bureau Trip Sheet", bts_name)
			bts.flags.ignore_validate_update_after_submit = True
			for i, row in enumerate(bts.settlement_journal_entries or []):
				if row.journal_entry == doc.name:
					bts.settlement_journal_entries.pop(i)
					break
			bts.save(ignore_permissions=True)

	# This method is called when the Journal Entry is canceled.
	# Updates the 'is_paid' field in the Substitute Booking.
	substitute_booking_name = doc.substitute_booking_reference
	if substitute_booking_name:
		# Fetch the related Substitute Booking document
		substitute_booking = frappe.get_doc('Substitute Booking', substitute_booking_name)

		# Uncheck 'is_paid' in Substitute Booking
		substitute_booking.db_set('is_paid', 0)
		substitute_booking.save()

		# Display success message
		frappe.msgprint(_("Journal Entry cancelled, and Substitute Booking updated successfully."))

	else:
		# Handle case where no Substitute Booking is linked
		frappe.msgprint(_("No Substitute Booking linked to this Journal Entry."))
