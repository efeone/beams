// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Auditing', {
    validate: function(frm) {
        if (frm.doc.asset_photos.length < 3) {
            frappe.throw(__('Please upload at least 3 photos of Asset'));
        }
    }
});
