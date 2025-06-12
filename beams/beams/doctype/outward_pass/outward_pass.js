// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on("Outward Pass", {
    bundles: function (frm) {
        if (frm.doc.bundles.length > 0) {
            let bundle_names = frm.doc.bundles.map((bundle) => bundle.asset_bundle);

            frappe.call({
                method: "beams.beams.doctype.outward_pass.outward_pass.bundle_asset_fetch",
                args: {
                    names: bundle_names,
                },
                callback: function (r) {
                    if (r.message) {
                        let existing_assets = frm.doc.assets || [];
                        let new_assets = r.message[0];

                        let merged_assets = mergeArrays(existing_assets, new_assets, "asset");
                        frm.set_value("assets", merged_assets);

                        let new_bundles = [];
                        for (let i = 0; i < r.message[1].length; i++) {
                            new_bundles.push({ "asset_bundle": r.message[1][i] });
                        }
                        frm.set_value("bundles", new_bundles);
                    }
                },
            });
        }
    },
    scan_bundle: function (frm) {
        if (!frm.doc.scan_bundle) {
            frappe.msgprint(__('Please ensure a bundle is scanned.'));
            return;
        }

        let scanned_value = frm.doc.scan_bundle.trim();

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Asset Bundle",
                name: scanned_value,
                fields: ["name", "assets"]
            },
            callback: function (r) {
                if (r.message) {
                    let asset_bundle = r.message;
                    let existing_bundle = (frm.doc.bundles || []).find(
                        row => row.asset_bundle === asset_bundle.name
                    );

                    if (!existing_bundle) {
                        let new_row = frm.add_child("bundles");
                        new_row.asset_bundle = asset_bundle.name;
                        frm.refresh_field("bundles");

                        if (asset_bundle.assets && asset_bundle.assets.length > 0) {
                            let existing_assets = frm.doc.assets || [];
                            let new_assets = asset_bundle.assets.map(asset => ({ asset: asset.asset }));
                            let merged_assets = [...existing_assets];
                            new_assets.forEach(new_asset => {
                                if (!merged_assets.some(existing => existing.asset === new_asset.asset)) {
                                    merged_assets.push(new_asset);
                                }
                            });

                            frm.set_value("assets", merged_assets);
                            frm.refresh_field("assets");
                        } else {
                            frappe.msgprint(__('No assets found in this bundle!'));
                        }
                    } else {
                        frappe.msgprint(__('Bundle is already added!'));
                    }

                    frm.set_value("scan_bundle", "");
                } else {
                    frappe.msgprint(__('No bundle found with this QR code!'));
                }
            },
            error: function (err) {
                frappe.msgprint(__('Error occurred while fetching bundle: ') + err.message);
            }
        });
    },
    scan_asset: function (frm) {
        if (!frm.doc.scan_asset) {
            frappe.msgprint(__('Please scan an asset.'));
            return;
        }
        let scanned_asset = frm.doc.scan_asset.trim();
        let existing_assets = frm.doc.assets || [];
        let already_exists = existing_assets.some(row => row.asset === scanned_asset);

        if (already_exists) {
            frappe.msgprint(__('This asset is already added.'));
        } else {
            let new_row = frm.add_child("assets");
            new_row.asset = scanned_asset;
            frm.refresh_field("assets");
        }
        frm.set_value("scan_asset", "");
    }
});

function mergeArrays(arr1, arr2, key) {
    const merged = [...arr1, ...arr2];
    const unique = merged.filter((obj, index, self) =>
        index === self.findIndex((o) => o[key] === obj[key])
    );
    return unique;
}
