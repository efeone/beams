// // Copyright (c) 2025, efeone and contributors
// // For license information, please see license.txt

frappe.ui.form.on("External Resource Request", {
    refresh(frm) {
        // Show the 'Purchase Invoice' button only if the document is submitted (docstatus == 1)
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Purchase Invoice'), function () {
                let invoice = frappe.model.get_new_doc("Purchase Invoice");
                invoice.posting_date = frm.doc.posting_date;
                frappe.set_route("form", "Purchase Invoice", invoice.name);
            }, __("Create"));
        }
    },

    required_from(frm) {
        update_required_resources(frm, 'required_from');
    },

    required_to(frm) {
        update_required_resources(frm, 'required_to');
    },
    required_from: function (frm) {
        frm.call("validate_required_from_and_required_to");
    },
    required_to: function (frm) {
        frm.call("validate_required_from_and_required_to");
    }
});

function update_required_resources(frm, fieldname) {
    // Ensure at least one row exists in the child table
    if (!frm.doc.required_resources || frm.doc.required_resources.length === 0) {
        frappe.model.add_child(frm.doc, 'required_resources');
    }

    // Update the child table field with the parent field value
    frm.doc.required_resources.forEach(row => {
        row[fieldname] = frm.doc[fieldname];
    });

    // Refresh the child table to reflect the changes
    frm.refresh_field('required_resources');
}
