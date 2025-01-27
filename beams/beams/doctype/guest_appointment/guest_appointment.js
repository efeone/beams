// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Guest Appointment', {
    refresh: function(frm) {
        // Add a button to the 'Create' group to create a new Event
        frm.add_custom_button(__('Event'), function() {
            // Create a new Event DocType (empty Event)
            frappe.new_doc('Event', {
                guest_appointment: frm.doc.name  // Optionally link the Event to this Guest Appointment
            });
        }, 'Create');  // Add the button under the 'Create' group
    }
});
