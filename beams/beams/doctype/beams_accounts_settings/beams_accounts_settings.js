// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Beams Accounts Settings", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Beams Accounts Settings', {
    setup: function(frm) {
        frm.set_query('doc_type', 'beams_naming_rule', function() {
            return {
                filters: {
                    name: ['in', ['Quotation', 'Sales Order', 'Sales Invoice']]
                }
            };
        });
    },
});
