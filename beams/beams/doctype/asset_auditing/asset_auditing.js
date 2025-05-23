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
    },
    posting_date:function (frm){
      frm.call("validate_posting_date");
    },
    scan_qr_code: function(frm) {
        if (frm.doc.scan_qr_code) {
            frappe.db.get_value('Asset', frm.doc.scan_qr_code, 'name')
                .then(r => {
                    if (r && r.message) {
                        frm.set_value('asset', r.message.name);
                    } else {
                        frappe.msgprint(__('Asset not found for scanned QR code'));
                        frm.set_value('asset', null);
                    }
                    frm.set_value('scan_qr_code', null);
                });
        }
    }
});
