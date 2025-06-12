frappe.ui.form.on('Full and Final Statement', {
    employee: function(frm) {
        if (frm.doc.employee) {
            fetch_asset_bundles(frm);
        }
    }
});

function fetch_asset_bundles(frm) {
    frappe.call({
        method: 'beams.beams.custom_scripts.full_and_final_statement.full_and_final_statement.fetch_asset_bundles_for_employee',
        args: {
            employee: frm.doc.employee
        },
        callback: function (r) {
            if (r.message && r.message.length > 0) {
                frm.clear_table('allocated_bundles');
                r.message.forEach(bundle => {
                    let row = frm.add_child('allocated_bundles');
                    row.asset_transfer_request = bundle.asset_transfer_request;
                    row.asset_bundle = bundle.asset_bundle;
                    row.date = bundle.date;
                    row.description = bundle.description;
                });

                frm.refresh_field('allocated_bundles');
            } else {
                frappe.msgprint(__('No allocated bundles found for this employee.'));
            }
        }
    });
}
