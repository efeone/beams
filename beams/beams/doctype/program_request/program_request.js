// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Program Request', {
  program_name: function(frm) {
        if (!frm.doc.program_name) return;

        frappe.call({
            method: "beams.beams.doctype.program_request.program_request.check_program_name_exists",
            args: { program_name: frm.doc.program_name },
            callback: function(response) {
                if (response.message) {
                    frappe.msgprint(__("A Program with this name already exists. Please choose a different name."));
                    frm.set_value("program_name", "");
                }
            }
        });
    },
    start_date: function (frm) {
        frm.call("validate_start_date_and_end_dates");
    },
    end_date: function (frm) {
        frm.call("validate_start_date_and_end_dates");
    },
    validate: function(frm) {
        if (frm.doc.generates_revenue && frm.doc.expected_revenue <= 0) {
            frappe.msgprint(__('Expected Revenue must be greater than 0.'));
            frappe.validated = false;  // Prevent saving the form
        }
    }  
});
