// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on('Training Request', {
    refresh: function(frm) {
        if (!frm.is_new() && frappe.user.has_role("HR Manager")) {
            frm.add_custom_button(__('Training Event'), () => {
                // Create a new Training Event
                frappe.model.with_doctype('Training Event', function() {
                    let training_event = frappe.model.get_new_doc('Training Event');
                    training_event.training_request = frm.doc.name;
                    // Add the employee from Training Request to the child table in Training Event
                    if (frm.doc.employee) {
                        let child = frappe.model.add_child(training_event, 'employees');
                        child.employee = frm.doc.employee;
                        child.training_request = frm.doc.name;
                    }
                    // Open the new Training Event document
                    frappe.set_route('Form', 'Training Event', training_event.name);
                });
            }, __('Create'));
        }
    }
});
