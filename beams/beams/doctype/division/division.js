// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Division', {
    onload: function(frm) {
        set_department_filter(frm);
    },
    company: function(frm) {
        set_department_filter(frm);
    }
});

function set_department_filter(frm) {
    if (frm.doc.company) {
        frm.set_query('department', function() {
            return {
                filters: {
                    'company': frm.doc.company
                }
            };
        });
    }
}
