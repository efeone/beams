
frappe.ui.form.on('Training Program', {
    validate: function(frm) {
        // Validate Email Format
        if (frm.doc.trainer_email && !frappe.utils.validate_type(frm.doc.trainer_email, "email")) {
            frappe.msgprint(__('Please enter a valid email address'));
            frappe.validated = false;
        }

        // Validate Contact Number (Only 10-digit numbers)
        if (frm.doc.contact_number && !/^\d{10}$/.test(frm.doc.contact_number)) {
            frappe.msgprint(__('Please enter a valid 10-digit contact number'));
            frappe.validated = false;
        }
    }
});
