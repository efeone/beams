// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cost Subhead", {
    refresh(frm) {
      frm.fields_dict.accounts.grid.get_field("default_account").get_query = function(doc, cdt, cdn) {
          let row = locals[cdt][cdn];
          return {
              filters: {
                  is_group: 0,
                  company: row.company
              }
          };
      };
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
