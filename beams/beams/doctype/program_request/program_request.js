// // Copyright (c) 2025, efeone and contributors
// // For license information, please see license.txt

frappe.ui.form.on('Program Request', {
    refresh: function (frm) {
        // Check if a Project exists for this Program Request
        if (frm.doc.workflow_state === 'Approved') {
            frappe.call({
                method: 'beams.beams.doctype.program_request.program_request.check_project_exists',
                args: { program_request_id: frm.doc.name },
                callback: function (r) {
                    if (!r.message) {
                        // Add the "Create Project" button if no project exists
                        frm.add_custom_button(__('Create Project'), function () {
                            frappe.call({
                                method: 'beams.beams.doctype.program_request.program_request.create_project_from_program_request',
                                args: { program_request_id: frm.doc.name },
                                callback: function (r) {
                                    if (r.message) {
                                        frappe.set_route('Form', 'Project', r.message);
                                    }
                                }
                            });
                        }).addClass('btn-primary');
                    }
                }
            });
        }
    },
    start_date: function (frm) {
        frm.call("validate_start_date_and_end_dates");
    },
    end_date: function (frm) {
        frm.call("validate_start_date_and_end_dates");
    }
});
