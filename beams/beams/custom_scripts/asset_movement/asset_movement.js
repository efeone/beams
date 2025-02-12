frappe.ui.form.on('Asset Movement', {
    onload: function(frm) {
        frm.set_query('reference_doctype', function() {
            return { filters: {} };
        });


        frm.set_query('reference_name', function() {
            return { filters: {} };
        });
    }
});
