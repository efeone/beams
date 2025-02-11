// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Technical Request', {
    refresh: function(frm) {
        // Initially hide the "Reason for Rejection" field
        frm.set_df_property("reason_for_rejection", "hidden", true);
        frm.set_df_property("employee", "read_only", false);
        frm.set_df_property("employee", "hidden", false);

        if (frm.doc.workflow_state === "Pending Approval" || frm.doc.workflow_state === "Draft") {
            frm.set_df_property("employee", "read_only", false);
        } else {
            frm.set_df_property("employee", "read_only", true);
        }

        set_employee_query(frm);
        toggle_reason_for_rejection_field(frm);

        if (!frm.is_new() && frm.doc.workflow_state === "Approved") {
            frm.add_custom_button("External Resource Request", function() {
                frappe.call({
                    method: "beams.beams.doctype.technical_request.technical_request.map_external_resource_request",
                    args: {
                        "technical_request": frm.doc.name
                    },
                    callback: function(response) {
                        if (response.message) {
                            frappe.set_route("Form", "External Resource Request", response.message);
                        }
                    },
                });
            }, "Create");
        }
      },
    posting_date:function (frm){
        frm.call("validate_posting_date");
      },

    required_employees: function(frm) {
        set_employee_query(frm);
        validate_employee_selection(frm);
    },

    designation: function(frm) {
        set_employee_query(frm);
    },

    workflow_state: function(frm) {
        // Trigger visibility logic when the workflow state changes
        toggle_reason_for_rejection_field(frm);
    },

    // Trigger validation when the "required_from" field is updated
    required_from: function(frm) {
        frm.call("validate_required_from_and_required_to");
    },

    required_to: function(frm) {
        frm.call("validate_required_from_and_required_to");
    }
});


// Function to validate the number of selected employees
function validate_employee_selection(frm) {
    let selected_employees = frm.doc.required_employees || [];
    let max_allowed = frm.doc.no_of_employees || 0;

    if (selected_employees.length > max_allowed) {
        frappe.msgprint({
            title: __('Message'),
            message: __('You can select a maximum of {0} employees.', [max_allowed])
        });

        while (selected_employees.length > max_allowed) {
            selected_employees.pop();
        }
        frm.refresh_field('required_employees');
    }
}

function set_employee_query(frm) {
    frm.fields_dict['required_employees'].get_query = function() {
        return {
            filters: {
                department: frm.doc.department,
                designation: frm.doc.designation
            }
        };
    };
}

function toggle_reason_for_rejection_field(frm) {
    if (!frm.doc.department) return; // Ensure department is set

    // Fetch the HOD for the selected department
    frappe.db.get_value('Department', frm.doc.department, 'head_of_department').then((r) => {
        if (r && r.message && r.message.head_of_department) {
            let hod_employee = r.message.head_of_department;

            frappe.db.get_value('Employee', { name: hod_employee }, 'user_id').then((user) => {
                if (user && user.message && user.message.user_id) {
                    const hod_user_id = user.message.user_id;
                    const is_hod = frappe.session.user === hod_user_id;

                    // Always show the "Reason for Rejection" field to the HOD
                    if (is_hod) {
                        frm.set_df_property("reason_for_rejection", "hidden", false);
                        frm.set_df_property("reason_for_rejection", "read_only", false);
                    } else {
                        // Hide the field for non-HOD users unless the workflow state is "Rejected"
                        if (frm.doc.workflow_state === "Rejected") {
                            frm.set_df_property("reason_for_rejection", "hidden", false);
                            frm.set_df_property("reason_for_rejection", "read_only", true);
                        } else {
                            frm.set_df_property("reason_for_rejection", "hidden", true);
                        }
                    }
                }
            });
        }
    });
}
