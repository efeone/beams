// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Visit Request', {
    request_date: function (frm) {
        frm.call("validate_request_date");
    },
});
