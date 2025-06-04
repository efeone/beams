// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt


frappe.ui.form.on("Makeup Consumption Entry", {
    // Filter on the item_code field to list only items from the selected item group with is_makeup_item checked
    onload: function (frm) {
      frappe.call({
        method: "frappe.client.get_value",
        args: {
          doctype: "BEAMS Admin Settings",
          fieldname: "item_group"
        },
        callback: function (r) {
          if (r.message) {
            var item_group = r.message.item_group;

            frm.fields_dict.items.grid.get_field("item_code").get_query = function () {
              return {
                filters: {
                  item_group: item_group,
                  is_makeup_item: 1
                }
              };
            };
          }
        }
      });
    }
  });
