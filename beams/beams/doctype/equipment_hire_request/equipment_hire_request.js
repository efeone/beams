// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Hire Request", {
    refresh(frm) {
      frm.add_custom_button(__('Purchase Invoice'), function () {
          var invoice = frappe.model.get_new_doc("Purchase Invoice");
          invoice.posting_date = frm.doc.posting_date;
          frappe.set_route("form", "Purchase Invoice", invoice.name);
      }, __("Create"));
    },
});
