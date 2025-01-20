// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on("Transportation Request", {
	refresh(frm) {
    frm.add_custom_button(__('Purchase Invoice'), function (){

    }, __("create"));

	},
});


frappe.ui.form.on("Transportation Request", {
    refresh(frm) {
        if (!frm.is_new()) {
            // Show the child table if the form is saved
            frm.set_df_property("vehicles", "hidden", false);
        } else {
            // Hide the child table if the form is new
            frm.set_df_property("vehicles", "hidden", true);
        }

        // Update the count of "No. of Own Vehicles"
        update_no_of_own_vehicles(frm);
    }
});

frappe.ui.form.on("Vehicles", {
    // Trigger when a row is added to the "Vehicles" child table
    vehicles_add(frm) {
        update_no_of_own_vehicles(frm);
    },
    // Trigger when a row is removed from the "Vehicles" child table
    vehicles_remove(frm) {
        update_no_of_own_vehicles(frm);
    }
});

// to update the "No. of Own Vehicles" field
function update_no_of_own_vehicles(frm) {
    // Calculate the total number of rows in the "Vehicles" table
    const count = frm.doc.vehicles ? frm.doc.vehicles.length : 0;

    // Update the "No. of Own Vehicles" field
    frm.set_value("no_of_own_vehicles", count);
    frm.refresh_field("no_of_own_vehicles");
}
