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

      if (frm.doc.workflow_state === "Approved") {
      // Add a button for 'Inward Register' only when workflow state is 'Approved'
      frm.add_custom_button(__('Inward Register'), function() {
        // Call a custom server-side method to create the Inward Register
        frappe.call({
            method: 'beams.beams.doctype.guest_appointment.guest_appointment.create_inward_register',
            args: {
                guest_appointment: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    frappe.set_route('Form', 'Inward Register', r.message.name);
                }
            }
        });
    }, __("Create"));
}

}
});
