frappe.ui.form.on('Vehicle', {
    refresh: function(frm) {
        frm.set_query('vehicle_safety_inspection', () => {
            return {
                filters: {
                    vehicle: frm.doc.name
                }
            };
        });
    }
});
