frappe.ui.form.on('Stringer Bill', {
    onload: function(frm) {
      /*
      * Set a query filter for the 'supplier' field to only show suppliers with 'is_stringer' set to 1
      */
        frm.set_query('supplier', function() {
            return {
                filters: {
                    'is_stringer': 1
                }
            };
        });
    },
});
