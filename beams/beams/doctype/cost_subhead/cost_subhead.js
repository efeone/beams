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
        });
        frm.add_custom_button(__('Update Budget Template'), function() {
            frappe.call({
                method: "beams.beams.doctype.cost_subhead.cost_subhead.update_budget_templates",
                args: {
                    cost_subhead: frm.doc.name
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(__('Budget Templates updated successfully'));
                    }
                }
            });
        });
    }
});
