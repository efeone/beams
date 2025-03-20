// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Technical Request', {
    refresh: function(frm) {
        // Initially hide the "Reason for Rejection" field
        frm.set_df_property("employee", "read_only", false);
        frm.set_df_property("employee", "hidden", false);

        if (frm.doc.workflow_state === "Pending Approval" || frm.doc.workflow_state === "Draft") {
            frm.set_df_property("employee", "read_only", false);
        } else {
            frm.set_df_property("employee", "read_only", true);
        }

        set_employee_query(frm);

        if (!frm.is_new() && frm.doc.workflow_state === "Approved") {
            frm.add_custom_button("External Resource Request", function() {
                frappe.call({
                    method: "beams.beams.doctype.technical_request.technical_request.create_external_resource_request",
                    args: {
                          technical_request: frm.doc.name
                      },
                      callback: function(response) {
                          if (response.message) {
                              frappe.set_route("Form", "External Resource Request", response.message);
                          }
                      }
                  });
              }, __("Create"));
        }
      },
    posting_date:function (frm){
        frm.call("validate_posting_date");
      },

    required_employees: function(frm) {
        set_employee_query(frm);
    },

    designation: function(frm) {
        set_employee_query(frm);
    },

    // Trigger validation when the "required_from" field is updated
    required_from: function(frm) {
        frm.call("validate_required_from_and_required_to");
    },

    required_to: function(frm) {
        frm.call("validate_required_from_and_required_to");
    }
});

function set_employee_query(frm) {
    let current_user = frappe.session.user;

    frm.fields_dict['required_employees'].grid.get_field("employee").get_query = function(doc, cdt, cdn) {
        let child = locals[cdt][cdn];

        // Get all selected employees
        let selected_employees = (doc.required_employees || []).map(row => row.employee).filter(emp => emp);

        return {
            filters: {
                department: child.department,
                designation: child.designation,
                name: ["not in", selected_employees] // Exclude already selected employees
            }
        };
    };
}
