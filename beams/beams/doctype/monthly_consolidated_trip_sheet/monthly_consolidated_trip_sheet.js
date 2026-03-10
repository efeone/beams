// Copyright (c) 2026, efeone and contributors
// For license information, please see license.txt


frappe.ui.form.on('Monthly Consolidated Trip Sheet', {
    onload(frm) {
        set_yeat(frm);
        set_supplier_filter(frm);
    }
});

// Set default year to current year on new document creation
function set_yeat(frm) {
    if (frm.is_new()) {
        frm.set_value("year", frappe.datetime.get_today().split("-")[0]);
    }
}

// Filter supplier field to show only transporters
function set_supplier_filter(frm) {
    frm.set_query("supplier", function() {
        return {
            filters: {
                is_transporter: 1
            }
        }
    })
}