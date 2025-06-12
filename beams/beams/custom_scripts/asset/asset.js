frappe.ui.form.on('Asset', {
    refresh: function(frm) {
        // Filter for shelf based on selected room
        frm.set_query('shelf', function() {
            return {
                filters: {
                    'room': frm.doc.room
                }
            };
        });

        // Filter for row based on selected shelf
        frm.set_query('row', function() {
            return {
                filters: {
                    'shelf': frm.doc.shelf
                }
            };
        });

        // Filter for bin based on selected row
        frm.set_query('bin', function() {
            return {
                filters: {
                    'row': frm.doc.row
                }
            };
        });
    },
});

