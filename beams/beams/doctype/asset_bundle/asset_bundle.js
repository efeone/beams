// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Bundle", {
	refresh:function(frm) {
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
										console.log('yoyo',selected_bundles)

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
  bundles: function (frm) {
        if (frm.doc.bundles.length > 0) {
            let bundle_names = frm.doc.bundles.map((bundle) => bundle.asset_bundle);
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
    },
});

function mergeArrays(arr1, arr2, key) {
  const merged = [...arr1, ...arr2];
  const unique = merged.filter((obj, index, self) =>
      index === self.findIndex((o) => o[key] === obj[key])
  );
  return unique;
}
