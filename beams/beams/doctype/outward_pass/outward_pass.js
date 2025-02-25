// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Outward Pass", {
bundles: function (frm) {
    if (frm.doc.bundles.length > 0) {
        let bundle_names = frm.doc.bundles.map((bundle) => bundle.asset_bundle);
        console.log("Fetching Assets for Bundles:", bundle_names);

        frappe.call({
            method: "beams.beams.doctype.outward_pass.outward_pass.bundle_asset_fetch",
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
