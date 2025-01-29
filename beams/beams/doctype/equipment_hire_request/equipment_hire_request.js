// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Hire Request", {
    refresh(frm) {
        // Show the 'Purchase Invoice' button only if the document is submitted (docstatus == 1) and approved
        if (frm.doc.docstatus == 1 && frm.doc.workflow_state == 'Approved') {

            // Create 'Purchase Invoice' button
            frm.add_custom_button(__('Purchase Invoice'), function () {
                let invoice = frappe.model.get_new_doc("Purchase Invoice");
                invoice.posting_date = frm.doc.posting_date; // Set posting date from the current document
                frappe.set_route("form", "Purchase Invoice", invoice.name); // Redirect to the new Purchase Invoice form
            }, __("Create"));

            // Create 'Asset Movement' button
            frm.add_custom_button(__('Asset Movement'), function () {
                let asset_movement = frappe.model.get_new_doc("Asset Movement");
                asset_movement.posting_date = frm.doc.posting_date; // Set posting date from the current document
                frappe.set_route("form", "Asset Movement", asset_movement.name); // Redirect to the new Asset Movement form
            }, __("Create"));
        }
    },
    required_from: function (frm) {
        frm.call("validate_required_from_and_required_to");
    },
    required_to: function (frm) {
        frm.call("validate_required_from_and_required_to");
    }
});
