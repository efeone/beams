frappe.ui.form.on('Driver', {
    onload: function(frm) {
        update_mandatory_fields(frm)
    },

    is_internal: function(frm) {
      update_mandatory_fields(frm)
    }
});

// Function to update the mandatory fields 'employee' and 'transporter' based on 'is_internal'
function update_mandatory_fields(frm) {
    // If 'is_internal' is checked, make 'employee' mandatory and 'transporter' optional
    frm.set_df_property('employee', 'reqd', frm.doc.is_internal ? true : false);
    frm.set_df_property('transporter', 'reqd', frm.doc.is_internal ? false : true);

}
