// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Guest Appointment', {
  refresh: function (frm) {
    // Add a button to the 'Create' group to create a new Event
    if (frm.doc.workflow_state === "Approved") {
      frm.add_custom_button(__('Event'), function () {
        // Create a new Event DocType (empty Event)
        frappe.new_doc('Event', {
          guest_appointment: frm.doc.name,
          subject : frm.doc.purpose_of_visit,
        });
      }, 'Create');  // Add the button under the 'Create' group

      frm.add_custom_button(__('Inward Register'), function () {
        frappe.call({
          method: 'beams.beams.doctype.guest_appointment.guest_appointment.create_inward_register',
          args: {
            guest_appointment: frm.doc.name
          },
          callback: function (r) {
            if (r.message) {
              frappe.db.get_doc('Inward Register', r.message).then(doc => {
                frappe.new_doc('Inward Register', doc);
              });
            }
          }
        });
      }, __("Create"));
    }
  },
  posting_date: function (frm) {
    frm.call("validate_posting_date");
  }
});
