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
    refresh: function (frm) {
        calculate_total(frm);
    }
});

frappe.ui.form.on('Stringer Bill Detail', {
    stringer_amount: function (frm) {
        calculate_total(frm);
    },
    stringer_bill_detail_remove: function (frm) {
        calculate_total(frm);
    }
});

function calculate_total(frm) {
    let total = 0;
    (frm.doc.stringer_bill_detail || []).forEach(row => {
        total += row.stringer_amount || 0;  // Summing up child table amounts
    });
    frm.set_value('stringer_amount', total);
}
