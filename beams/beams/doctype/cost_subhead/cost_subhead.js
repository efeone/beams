// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cost Subhead", {
    refresh(frm) {
        frm.set_query('default_account','accounts', () => {
            return {
                filters: {
                    is_group: 0
                }
            }
        })
    }
});
