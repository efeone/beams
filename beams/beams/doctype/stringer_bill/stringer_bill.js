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
frappe.ui.form.on('Stringer Bill Date', {
    date: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        // Get the list of dates from the child table
        let dates = frm.doc.date.map(row => row.date);
        // Check for duplicate dates
        if (dates.filter(d => d === child.date).length > 1) {
            frappe.msgprint({
                title: __('Message'),
                message: __('{0} Date should be Unique', [child.date]),
                indicator: 'red'
            });
            frappe.model.set_value(cdt, cdn, 'date', '');
            return;
        }
        // Calculate the number of unique dates and update the no_of_days field
        update_no_of_days(frm);
    },
    date_remove: function(frm) {
        // Recalculate no_of_days when a row is removed
        update_no_of_days(frm);
    }
});

/*
* Helper function to update the no_of_days field
*/
function update_no_of_days(frm) {
    let dates = frm.doc.date.map(row => row.date);
    let unique_dates = [...new Set(dates)];
    frm.set_value('no_of_days', unique_dates.length);
}
