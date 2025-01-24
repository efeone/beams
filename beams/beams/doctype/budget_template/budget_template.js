// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Template', {
    department: function(frm) {
        let selected_department = frm.doc.department;
        if (selected_department) {
            frm.fields_dict['budget_template_item'].grid.get_field('cost_sub_head').get_query = function(doc, cdt, cdn) {
                return {
                    filters: {
                        department: selected_department
                    }
                };
            };
            frm.set_query('division', function() {
                return {
                    filters: {
                        department: selected_department
                    }
                };
            });
        } else {
            frm.fields_dict['budget_template_item'].grid.get_field('cost_sub_head').get_query = function(doc, cdt, cdn) {
                return {};
            };

            frm.set_query('division', function() {
                return {};
            });
            frm.clear_table('budget_template_item');
            frm.refresh_field('budget_template_item');
        }
    }
});


frappe.ui.form.on('Budget Template Item', {
    cost_sub_head: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        if (row.cost_sub_head) {
            frappe.db.get_value('Cost Subhead', row.cost_sub_head, ['account'], function(value) {
                if (value) {
                    frappe.model.set_value(cdt, cdn, 'account', value.account);
                }
            });
        }
    }
});
