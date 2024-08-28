frappe.ui.form.on('Driver', {
    onload: function(frm) {
        // Set the 'transporter' field as mandatory by default
        frm.set_df_property('transporter', 'reqd', true);

        toggle_mandatory_fields(frm);
    },

    // Triggered when the 'is_internal' checkbox is changed
    is_internal: function(frm) {
        // Update the mandatory fields based on the 'is_internal' value
        toggle_mandatory_fields(frm);
    }
});

// Function to toggle the mandatory fields 'employee' and 'transporter' based on 'is_internal'
function toggle_mandatory_fields(frm) {
    // If 'is_internal' is checked, make 'employee' mandatory and 'transporter' optional
    if (frm.doc.is_internal) {
        frm.set_df_property('employee', 'reqd', true);
        frm.set_df_property('transporter', 'reqd', false);
    }
    // If 'is_internal' is unchecked, make 'transporter' mandatory and 'employee' optional
    else {
        frm.set_df_property('transporter', 'reqd', true);
        frm.set_df_property('employee', 'reqd', false);
    }

    frm.refresh_field('employee');
    frm.refresh_field('transporter');
}
