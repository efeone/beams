// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on("Transportation Request", {
    refresh: function (frm) {
        if (frm.doc.workflow_state === "Approved") {
            frm.add_custom_button(__('Vehicle Hire Request'), function () {
                frappe.model.open_mapped_doc({
                    method: 'beams.beams.doctype.transportation_request.transportation_request.map_transportation_to_vehicle',
                    frm: frm,
                });
            }, __("Create"));
        }

        if (frm.doc.workflow_state === "Pending Approval") {
            frm.set_df_property("vehicles", "read_only", false);
        } else {
            frm.set_df_property("vehicles", "read_only", true);
        }
    },
    posting_date:function (frm){
        frm.call("validate_posting_date");
      },

    vehicles_add: function (frm, cdt, cdn) {
        frm.set_value("no_of_own_vehicles", frm.doc.vehicles.length);
    },
    vehicles_remove: function (frm, cdt, cdn) {
        frm.set_value("no_of_own_vehicles", frm.doc.vehicles.length);
    },
});
