// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Release Order", {
  delivery_date: function (frm) {
		$.each(frm.doc.items || [], function (i, d) {
			if (!d.delivery_date) d.delivery_date = frm.doc.delivery_date;
		});
		refresh_field("items");
	},
});

frappe.ui.form.on('Release Order Item', {
    item_code: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.item_code) {
            row.qty = 1;
            frm.refresh_field('items'); 
        }
    }
});
