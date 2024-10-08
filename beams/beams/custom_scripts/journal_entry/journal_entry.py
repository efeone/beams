import frappe
from frappe import _

def on_cancel(doc, method):
    """
    This method is called when the Journal Entry is canceled.
    and updates the 'is_paid' field in the Substitute Booking.
    """
    # Check if the Journal Entry is linked to a Substitute Booking
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
