frappe.ui.form.on('Project', {
    //function adds a button to the 'Project' form to create an Adhoc Budget.
    refresh: function (frm) {
        frm.add_custom_button(__('Adhoc Budget'), function () {
            frappe.model.open_mapped_doc({
                method: "beams.beams.custom_scripts.project.project.create_adhoc_budget",
                frm: frm,
            });
        }, __("Create"));
        // Adds a button to the 'Project' form to create an Transportation Request.
        frm.add_custom_button(__('Transportation Request'), function () {
            frappe.model.open_mapped_doc({
                method: "beams.beams.custom_scripts.project.project.create_transportation_request",
                frm: frm,
            });
        }, __("Create"));
    }
});
