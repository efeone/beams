// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Accounts', {
    company: function(frm, cdt, cdn) {
        set_account_query(frm);
    },
    accounts_add: function(frm, cdt, cdn) {
        set_account_query(frm);
    }
});

// Set query to filter 'default_account' based on the selected company
function set_account_query(frm) {
    frm.fields_dict['accounts'].grid.get_field("default_account").get_query = function(doc, cdt, cdn) {
        let row = locals[cdt][cdn];
        return {
            filters: {'company': row.company}
        };
    };
}
