// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Auditing', {
    refresh: function(frm) {
        if (frm.doc.bureau) {
            set_asset_filter(frm);
        }
    },

    bureau: function(frm) {
        handle_bureau_change(frm);
    }
});


/**
 * Handles logic when Bureau field value changes
 */
function handle_bureau_change(frm) {
    if (!frm.doc.bureau) return;

    set_asset_filter(frm);

    // Clear child table to avoid mismatched assets
    frm.clear_table('asset_auditing_detail');
    frm.refresh_field('asset_auditing_detail');
}


/**
 * Sets filter on Asset field in child table based on Bureau location
 */
function set_asset_filter(frm) {

    frm.fields_dict['asset_auditing_detail'].grid.get_field('asset').get_query = function() {
        return {
            filters: frm.doc.location
        };
    };
}

