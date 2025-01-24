// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inward Register", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {  // Show the button only if the document is submitted (docstatus === 1)
            frm.add_custom_button(__('Create Visitor Pass'), function () {
                frappe.new_doc("Visitor Pass", {
                    inward_register: frm.doc.name,  // Link the current Inward Register
                    issued_date: frappe.datetime.now_date(),  // Set default issued date to today
                    issued_time: frappe.datetime.now_time(),  // Set default issued time to now
                    issued_to: frm.doc.visitor_name  // Fetch the visitor name
                });
            });
        }
    }
});
