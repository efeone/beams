// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Auditing', {
    asset: function(frm) {
        if (frm.doc.asset) {
            frappe.db.get_value('Asset', frm.doc.asset, 'custodian', (r) => {
                if (r && r.custodian) {
                    frm.set_value('employee', r.custodian);
                }
            });
        }
    }
});
