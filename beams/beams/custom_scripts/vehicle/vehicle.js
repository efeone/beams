frappe.ui.form.on('Vehicle', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('New Vehicle Safety Inspection'), function () {
                frappe.new_doc('Vehicle Safety Inspection', {
                    vehicle: frm.doc.name
                });
            }, __('Create'));
        }
    }
});
