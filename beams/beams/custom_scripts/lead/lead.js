frappe.ui.form.on("Lead", {
    refresh: function (frm) {
        // Remove "Add to Prospect" button under "Action"
        setTimeout(() => {
            frm.remove_custom_button("Add to Prospect", "Action");
        }, 500);

        // Override the Opportunity creation process
        if (!frm.is_new()) {
            override_make_opportunity(frm);
        }
    }
});

function override_make_opportunity(frm) {
    // Remove default "Opportunity" button
    frm.remove_custom_button("Opportunity", "Create");

    // Add custom "Opportunity" button that creates Opportunity directly
    frm.add_custom_button(
        __("Opportunity"),
        function () {
            frappe.call({
                method: "erpnext.crm.doctype.lead.lead.make_opportunity",
                args: {
                    source_name: frm.doc.name,
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.set_route("Form", "Opportunity", r.message.name);
                    }
                },
                freeze: true,
                freeze_message: __("Creating Opportunity..."),
            });
        },
        __("Create")
    );
}
