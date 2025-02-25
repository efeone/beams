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

        if (frm.doc.asset_type === "Bundle" && frm.doc.bundle) {
            fetch_bundle_assets(frm);
        } else {
            frm.set_value('assets', []);
            frm.refresh_field('assets');
        }
    },
    asset_return_checklist_template: function(frm) {
        if (frm.doc.asset_return_checklist_template) {
          console.log("Fetching checklist items for template:", frm.doc.asset_return_checklist_template);
            frappe.call({
                method: "beams.beams.doctype.asset_transfer_request.asset_transfer_request.get_asset_return_checklist_template",
                args: {
                    template_name: frm.doc.asset_return_checklist_template
                },
                callback: function(response) {
                    if (response.message) {
                        frm.clear_table("aresponse.messageet_return_checklist");
                        response.message.forEach(item => {
                            let row = frm.add_child("asset_return_checklist");
                            row.checklist_item = item.checklist_item;
                        });
                        frm.refresh_field("asset_return_checklist");
                    }
                }
            });
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
                let asset_values = [];
                let bundle_values = [];
                response.message.forEach(function(item) {
                    var row = frm.add_child('items');
                    row.item = item.item;
                    row.uom = item.uom;
                    row.qty = item.qty;
                    asset_values.push(item.assets);
                    bundle_values.push(item.bundles);
                });
                frm.refresh_field('items');
                frm.set_value('assets', asset_values);
                frm.refresh_field('assets');
                frm.set_value('bundles', bundle_values);
                frm.refresh_field('bundles');
            }
        }
    });
}



function fetch_bundle_assets(frm) {
  frappe.call({
      method: "beams.beams.doctype.asset_transfer_request.asset_transfer_request.get_bundle_assets",
      args: { bundle: frm.doc.bundle },
      callback: function(response) {
          if (response.message && response.message.assets && response.message.bundles) {
              frm.set_value('assets', response.message.assets);
              frm.set_value('bundles', response.message.bundles);
          } else {
              frm.set_value('assets', []);
              frm.set_value('bundles', []);
          }
          frm.refresh_field('assets');
          frm.refresh_field('bundles');
      }
  });
}
