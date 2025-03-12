frappe.ui.form.on("Lead", {
    refresh: function (frm) {
        // Remove "Add to Prospect" button under "Action"
        setTimeout(() => {
            frm.remove_custom_button("Add to Prospect", "Action");
        }, 500);

        // Override Opportunity button
        if (!frm.is_new()) {
            override_make_opportunity(frm);
        }
    }
});

function override_make_opportunity(frm) {
    // Remove default "Opportunity" button
    frm.remove_custom_button("Opportunity", "Create");

    // Add custom "Opportunity" button without a dialog
    frm.add_custom_button(
        __("Opportunity"),
        function () {
            frappe.model.open_mapped_doc({
                method: "erpnext.crm.doctype.lead.lead.make_opportunity",
                frm: frm
            });
        },
        __("Create")
    );
}
