// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Bundle", {
    refresh:function(frm) {
      // Initialize QR Scanner only once
      if (!frm._qr_scanner_initialized) {
          frm._qr_scanner_initialized = true;
          frm.fields_dict.scan_qr_code.$wrapper.on("click", function() {
              let scanner = new frappe.ui.Scanner({
                  multiple: false,
                  on_success: function(result) {
                      let scanned_value = result.text.trim();
                      frm.set_value("scan_qr_code", scanned_value);
                      frm.trigger("scan_qr_code");  // Trigger processing
                  },
                  on_error: function(error) {
                      frappe.msgprint(__('Failed to scan QR Code. Try again!'));
                  }
              });
              scanner.show();
          });
      }

        frm.fields_dict['stock_items'].grid.get_field('item').get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    is_fixed_asset: 0
                }
            };
        };
        frappe.call({
            method: "beams.beams.doctype.asset_bundle.asset_bundle.get_selected_assets",
            callback: function (response) {
                if (response.message) {
                    let selected_assets = response.message;
                    frm.fields_dict['assets'].get_query = function () {
                        return {
                            filters: [
                                ['name', 'not in', selected_assets]
                            ]
                        };
                    };
                }
            }
        });
        frappe.call({
            method: "beams.beams.doctype.asset_bundle.asset_bundle.get_selected_bundles",
            callback: function (response) {
                if (response.message) {
                    let selected_bundles = response.message;
                    frm.fields_dict['bundles'].get_query = function () {
                        return {
                            filters: [
                                ['name', 'not in', selected_bundles]
                            ]
                        };
                    };
                }
            }
        });
    },
    validate: function(frm) {
        if (!frm.doc.stock_items?.length && !frm.doc.assets?.length && !frm.doc.bundles?.length) {
            frappe.msgprint(__('At least one of Stock Items, Assets, or Bundles must be filled in.'));
            frappe.validated = false;
        }
    },
    scan_qr_code: function(frm) {
    if (!frm.doc.scan_qr_code) return;

    let scanned_value = frm.doc.scan_qr_code.trim();

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Asset",
            filters: { name: scanned_value },
            fields: ["name", "asset_name"]
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let asset = r.message[0];
                let existing_asset = (frm.doc.assets || []).find(row => row.asset === asset.name);
                if (!existing_asset) {
                    let new_asset = frm.add_child("assets");
                    new_asset.asset = asset.name;
                    new_asset.asset_name = asset.asset_name;
                    frm.refresh_field("assets");
                } else {
                    frappe.msgprint(__('Asset is already added!'));
                }
            } else {
                frappe.msgprint(__('No asset found with this QR code!'));
            }
            frm.set_value("scan_qr_code", ""); // Clear scan field
        }
    });
    },

  bundles: function (frm) {
  let bundle_names = frm.doc.bundles.map((bundle) => bundle.asset_bundle);
    let previousBundles = frm.doc.__previous_bundles || [];
        if (frm.doc.bundles.length > 0) {
            frappe.call({
                method: "beams.beams.doctype.asset_bundle.asset_bundle.bundle_asset_fetch",
                args: {
                    names: bundle_names,
                },
                callback: function (r) {
                    if (r.message) {
                        let existing_assets = frm.doc.assets || [];
                        let new_assets = r.message[0];
                        let merged_assets = mergeArrays(existing_assets, new_assets, "asset")
                        frm.set_value("assets", merged_assets);
                        let new_bundles = []
                        for (var i = 0; i < r.message[1].length; i++) {
                          new_bundles.push({"asset_bundle":r.message[1][i]})
                        }
                        frm.set_value("bundles", new_bundles)
                    }
                },
            });
        }

  let removedBundles = previousBundles.filter(b => !bundle_names.includes(b));
   if (removedBundles.length > 0) {
   frappe.call({
   method: "beams.beams.doctype.asset_bundle.asset_bundle.bundle_asset_fetch",
   args: {
   names: removedBundles,
   },
   callback: function (r) {
   if (r.message) {
   let removed_assets = r.message[0];
   let updated_assets = frm.doc.assets.filter(asset =>
   !removed_assets.some(removed => removed.asset === asset.asset)
   );
   frm.set_value("assets", updated_assets);
   }
   },
   });
   }
   frm.doc.__previous_bundles = bundle_names;
    },
});

function mergeArrays(arr1, arr2, key) {
  const merged = [...arr1, ...arr2];
  const unique = merged.filter((obj, index, self) =>
      index === self.findIndex((o) => o[key] === obj[key])
  );
  return unique;
}
