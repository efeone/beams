// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on("Transportation Request", {
    refresh(frm) {
        // Show the "Purchase Invoice" button only if the status is "Approved"
        if (frm.doc.workflow_state === "Approved") {
            frm.add_custom_button(__('Purchase Invoice'), function () {
                var invoice = frappe.model.get_new_doc("Purchase Invoice");
                invoice.posting_date = frm.doc.posting_date;
                frappe.set_route("form", "Purchase Invoice", invoice.name);
            }, __("Create"));
        }

        // Show the "Vehicle Hire Request" button only if the status is "Approved"
        if (frm.doc.workflow_state === "Approved") {
            frm.add_custom_button(__('Vehicle Hire Request'), function () {
                frappe.model.open_mapped_doc({
                    method: 'beams.beams.doctype.transportation_request.transportation_request.map_transportation_to_vehicle',
                    frm: frm,
                });
            }, __("Create"));
        }

        // Show or hide the child table "vehicles" based on whether the form is new
        if (!frm.is_new()) {
            frm.set_df_property("vehicles", "hidden", false);
        } else {
            frm.set_df_property("vehicles", "hidden", true);
        }

    },
});
