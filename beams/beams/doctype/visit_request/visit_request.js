// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visit Request", {
    refresh(frm) {
        create_inward_register(frm);
    },
});

function create_inward_register(frm) {
    if (frm.doc.workflow_state === "Security Informed") {
        frm.add_custom_button("Inward Register", ()=> {
            frappe.new_doc("Inward Register", {
                visit_request       : frm.doc.name,
                visitor_type        : frm.doc.visitor_type,
                visitor_name        : frm.doc.visitor_name,
                purpose_of_visit    :frm.doc.purpose_of_visit
            });
    },__("Create"));
    }

}

