frappe.ui.form.on('Asset Movement', {
    onload: function(frm) {
        frm.set_query('reference_doctype', function() {
            return { filters: {} };
        });

        frm.set_query('reference_name', function() {
            return { filters: {} };
        });
    },
    refresh: function(frm) {
        // Filter for 'Shelf','Row' & 'Bin' field in assets child table
        frm.fields_dict.assets.grid.get_field('shelf').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                filters: {
                    'room': row.room
                }
            };
        };
        frm.fields_dict.assets.grid.get_field('row').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                filters: {
                    'shelf': row.shelf
                }
            };
        };
        frm.fields_dict.assets.grid.get_field('bin').get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                filters: {
                    'row': row.row
                }
            };
        };
    }

});
