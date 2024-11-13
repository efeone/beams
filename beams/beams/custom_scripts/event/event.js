frappe.ui.form.on('Event', {
    /**
     * Adds a custom button 'Training Request' for users with 'HOD' role
     * This button creates a new 'Training Request' document.
     */
    refresh: function(frm) {
        // Check if the document is saved (not new) and user has the 'HOD' role
        if (!frm.is_new() && frappe.user.has_role('HOD')) {
            // Add the 'Training Request' button in the 'Create' section
            frm.add_custom_button('Training Request', function() {
                // Creates a new 'Training Request' document
                frappe.new_doc('Training Request');
            }, 'Create');
        }
    }
});
