// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Program Request', {
    start_date: function (frm) {
        frm.call("validate_start_date_and_end_dates");
    },
    end_date: function (frm) {
        frm.call("validate_start_date_and_end_dates");
    },
    validate: function(frm) {
       if (frm.doc.generates_revenue && frm.doc.expected_revenue <= 0) {
           frappe.msgprint(__('Expected Revenue must be greater than 0.'));
           frappe.validated = false;  // Prevents form submission
       }
   }
});
