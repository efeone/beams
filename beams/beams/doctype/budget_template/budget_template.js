// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Template', {
    refresh: function (frm) {
        set_filters(frm);
    },
    department: function (frm) {
        set_filters(frm);
        if (!frm.doc.department) {
            frm.set_value('division',)
            frm.clear_table('budget_template_item');
            frm.refresh_field('budget_template_item');
        }
    }
});

frappe.ui.form.on('Budget Template Item', {
    cost_sub_head: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.cost_sub_head) {
            frappe.db.get_value('Cost Subhead', row.cost_sub_head, 'account').then(r => {
                frappe.model.set_value(cdt, cdn, 'account', r.message.account);
            })
        }
    }
});

function set_filters(frm) {
    frm.set_query('division', function () {
        return {
            filters: {
                department: frm.doc.department
            }
        };
    });
}
