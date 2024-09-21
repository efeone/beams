//  Copyright (c) 2024, efeone and contributors
//  For license information, please see license.txt


frappe.ui.form.on('Substitute Booking', {
    refresh: function(frm) {
        // Add "Leave Application" button under "View"
        frm.add_custom_button(__('Leave Application List'), function () {
            const employee = frm.doc.substituting_for;
            if (employee) {
                // Navigate to the Leave Application doctype for the specified employee
                frappe.set_route('Form', 'Leave Application', { employee: employee });
                }
            else {
                frappe.msgprint(__('Please specify an employee in the "Substituting For" field.'));
              }
            }, __("View"));
          }
        });
