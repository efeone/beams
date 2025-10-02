// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Revenue Centre", {
    onload: function(frm) {
        frm.set_query("account", function() {
            return {
                filters: {
                    account_type: "Income Account"
                }
            };
        });
    }
});
