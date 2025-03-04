// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Template', {
    refresh: function (frm) {
        set_filters(frm);
    },
    department: function (frm) {
        set_filters(frm);
        frm.set_value('division', null);
        if (!frm.doc.department) {
            frm.set_value('division',)
            frm.clear_table('budget_template_item');
            frm.refresh_field('budget_template_item');
        }
    },
    company: function (frm) {
        frm.set_value('department', null);
        frm.set_value('division', null);
        if (frm.doc.company) {
            // frm.clear_table("budget_template_item");
            frm.refresh_field("budget_template_item");
        }
    }
});

frappe.ui.form.on('Budget Template Item', {
    cost_sub_head: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        if (row.cost_sub_head && frm.doc.company) {
            frappe.db.get_doc('Cost Subhead', row.cost_sub_head).then(doc => {
                if (doc.accounts && doc.accounts.length > 0) {
                    let account_found = doc.accounts.find(acc => acc.company === frm.doc.company);
                    if (account_found) {
                        frappe.model.set_value(cdt, cdn, 'account', account_found.default_account);
                    } else {
                        frappe.model.set_value(cdt, cdn, 'account', '');
                        frappe.msgprint(__('No default account found for the selected Cost Subhead and Company.'));
                    }
                } else {
                    frappe.model.set_value(cdt, cdn, 'account', '');
                }
            });
        }
    }
});

function set_filters(frm) {
    frm.set_query('division', function () {
        return {
            filters: {
                department: frm.doc.department,
                company: frm.doc.company
            }
        };
    });
    frm.set_query('department', function () {
        return {
            filters: {
                company: frm.doc.company
            }
        };
    });
}
