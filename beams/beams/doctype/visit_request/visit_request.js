// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Visit Request', {
    request_date: function (frm) {
        frm.call({
            method: 'validate_request_date',
            doc: frm.doc
        });
    }
});
