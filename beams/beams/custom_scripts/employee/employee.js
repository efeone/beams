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
        }
    }
});
