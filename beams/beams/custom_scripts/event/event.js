frappe.ui.form.on('Event', {
    /**
     * Adds a custom button 'Training Request' for users with 'HOD' role
     * This button creates a new 'Training Request' document.
     */
    refresh: function(frm) {
        if (frappe.user.has_role('HOD')) {
            // Adds the custom button 'Training Request' in the 'Create' section
            frm.add_custom_button('Training Request', function() {
                // Creates a new 'Training Request' document
                frappe.new_doc('Training Request');
            }, 'Create');
        }
    }
});
