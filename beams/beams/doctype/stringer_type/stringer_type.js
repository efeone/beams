frappe.ui.form.on('Stringer Type', {
    onload: function(frm) {
        // Fetch items where is_stock_item is unchecked
        frm.set_query('item', function() {
            return {
                filters: {
                    'is_stock_item': 0  // Filter for items where the checkbox is unchecked (0)
                }
            };
        });
    }
});
