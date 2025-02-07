// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("External Resource Request", {
      required_from: function (frm) {
          frm.call('updated_required_resources',)
          .then(r => {
              if (r.message) {
                  frm.refresh_field("required_resources");
              }
          })
      },

      required_to: function (frm) {
        frm.call('updated_required_resources',)
        .then(r => {
            if (r.message) {
                frm.refresh_field("required_resources");
            }
        })
      }
    });

    frappe.ui.form.on("External Resources Detail", {
        required_resources_add: function (frm, cdt, cdn) {
          frm.call('updated_required_resources',)
          .then(r => {
              if (r.message) {
                  frm.refresh_field("required_resources");
              }
          })
        }
    });
