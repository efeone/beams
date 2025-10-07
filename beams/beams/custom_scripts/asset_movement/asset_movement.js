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

        asset_recevied_acknowledgement(frm);
        
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



function asset_recevied_acknowledgement(frm) {
    frm.clear_custom_buttons();

    const has_unacknowledged = (frm.doc.assets || []).some(row => !row.acknowledged);
    if (frm.doc.docstatus !== 1 || !has_unacknowledged) return;
    if (frappe.session.user !== frm.doc.user_id) return;


    const btn = frm.add_custom_button(__('Acknowledge Receipt'), () => {
        frappe.confirm(
            __('Are you sure you want to acknowledge receipt of these assets?'),
            () => {
                frappe.call({
                    method: "beams.beams.custom_scripts.asset_movement.asset_movement.acknowledge_assets",
                    args: {
                        asset_movement_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                            frm.reload_doc();
                        }
                    }
                });
            }
        );
    });

    btn.css({
        backgroundColor: '#2175b1ff',
        color: 'white',
        border: 'none',
        fontWeight: '500'
    });
}



