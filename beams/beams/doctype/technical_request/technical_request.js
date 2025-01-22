// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Technical Request', {
    refresh: function(frm) {
        // Initially hide the "Reason for Rejection" field
        frm.set_df_property("reason_for_rejection", "hidden", true);
        frm.set_df_property("employee", "read_only", false);
        frm.set_df_property("employee", "hidden", false);
        if (frm.doc.workflow_state === "Pending Approval" || frm.doc.workflow_state =='Draft') {
            frm.set_df_property("employee", "read_only", false);
        } else {
            frm.set_df_property('employee', 'read_only', true);
        }

        set_employee_query(frm)

        // Handle the visibility of the "Reason for Rejection" field
        toggle_reason_for_rejection_field(frm);
    },
    employee: function(frm) {
      console.log("here");
       set_employee_query(frm);
    },
    designation: function(frm) {
      set_employee_query(frm);
    },
    workflow_state: function(frm) {
        // Trigger visibility logic when the workflow state changes
        toggle_reason_for_rejection_field(frm);
    }
});

function set_employee_query(frm) {
  frm.set_query('employee', () => {
      return {
          filters: {
            department: frm.doc.department,
            designation: frm.doc.designation
          }
      }
  })
}

function toggle_reason_for_rejection_field(frm) {
    // Fetch the HOD for the selected department
    frappe.db.get_value('Department', frm.doc.department, 'head_of_department', (r) => {
        if (r && r.head_of_department) {
            frappe.db.get_value('Employee', {name: r.head_of_department}, 'user_id', (user) => {
                const hod_user_id = user.user_id;

                // Determine if the logged-in user is the HOD
                const is_hod = frappe.session.user === hod_user_id;

                // Always show the "Reason for Rejection" field to the HOD, even before the workflow state is "Rejected"
                if (is_hod) {
                    frm.set_df_property("reason_for_rejection", "hidden", false);

                    // Allow only HOD to edit the field
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
            });
        }
    });
}
