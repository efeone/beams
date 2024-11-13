frappe.ui.form.on('Employee', {
    /**
     * Adds a custom button 'Training Request' for users with 'HOD' role
     * This button creates a new 'Training Request' document and links it to the current employee.
     */
    refresh: function(frm) {
        if (frappe.user.has_role('HOD')) {
            // Adds the custom button 'Training Request' in the 'Create' section
            frm.add_custom_button('Training Request', function() {
                // Creates a new 'Training Request' document and sets the employee field
                frappe.new_doc('Training Request', {
                    employee: frm.doc.name
                });
            }, 'Create');

            frappe.call({
                method: "beams.beams.custom_scripts.employee.employee.get_employee_name_for_user",
                args: {
                    user_id: frappe.session.user
                },
                callback: function(response) {
                    if (response.message) {
                        frm.add_custom_button(__('Event'), function() {
                            frappe.model.open_mapped_doc({
                                method: "beams.beams.custom_scripts.employee.employee.create_event",
                                frm: frm,
                                args: {
                                    "employee_id": frm.doc.name,
                                    "hod_user": frappe.session.user
                                }
                            });
                        }, __('Create'));
                     }
                }
            });
    }
  }
});
