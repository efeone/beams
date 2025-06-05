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
        frm.trigger('toggle_asset_movement_item_fields');
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
    },
    purpose: function(frm) {
        // Call toggle_fields when purpose changes
        frm.trigger('toggle_asset_movement_item_fields');
    },

    toggle_asset_movement_item_fields: function(frm) {
        // Hide Room, Shelf, Row, and Bin fields in Asset Movement Item when purpose is 'Issue'
        const hide_fields = (frm.doc.purpose === 'Issue');

        frm.fields_dict.assets.grid.update_docfield_property('room', 'hidden', hide_fields);
        frm.fields_dict.assets.grid.update_docfield_property('shelf', 'hidden', hide_fields);
        frm.fields_dict.assets.grid.update_docfield_property('row', 'hidden', hide_fields);
        frm.fields_dict.assets.grid.update_docfield_property('bin', 'hidden', hide_fields);
    }
});
