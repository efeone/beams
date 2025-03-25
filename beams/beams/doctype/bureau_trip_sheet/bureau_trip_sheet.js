// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bureau Trip Sheet", {
    refresh: function (frm) {
        filter_supplier_field(frm);
    }

});

// Function to filter the supplier field
function filter_supplier_field(frm) {
    frm.set_query("supplier", function () {
        return {
            filters: {
                is_transporter: 1
            }
        };
    });
}
