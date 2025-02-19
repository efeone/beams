// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Transfer Request", {
    posting_date: function(frm) {
        frm.call("validate_posting_date");
    },

    bundle: function(frm) {
        if (frm.doc.asset_type === "Bundle" && frm.doc.bundle) {
            fetch_stock_items(frm);
        } else {
            frm.clear_table('items');
            frm.refresh_field('items');
        }
    }
});

function fetch_stock_items(frm) {
    frappe.call({
        method: "beams.beams.doctype.asset_transfer_request.asset_transfer_request.get_stock_items_from_bundle",
        args: {
            bundle: frm.doc.bundle
        },
        callback: function(response) {
            if (response.message) {
                frm.clear_table('items');
                let asset_values = []; // Declare the array to store item values
                let bundle_values = [];
                response.message.forEach(function(item) {
                    var row = frm.add_child('items');
                    row.item = item.item;
                    row.uom = item.uom;
                    row.qty = item.qty;

                    // Add item to asset_values for multi-select field
                    asset_values.push(item.assets);
                    bundle_values.push(item.bundles);
                });
                frm.refresh_field('items');

                // Set the asset values in the multi-select field
                frm.set_value('assets', asset_values);
                frm.refresh_field('assets');
                frm.set_value('bundles', bundle_values);
                frm.refresh_field('bundles');
            }
        }
    });
}
