frappe.ui.form.on('Training Event', {
    refresh: function(frm) {
      if (frm.doc.docstatus !== 1) {
        setTimeout(() => {
          frm.remove_custom_button('Training Result');
          frm.remove_custom_button('Training Feedback');
        }, 5);
      }
        if (!frm.is_new() && frappe.user.has_role("HR Manager")) {
            // Create the main group button "Training Request"
            frm.add_custom_button("Training Request", () => {
                show_training_request_dialog(frm);
            }, "Get Employees");
        }
    },

    training_program: function(frm) {
        if (frm.doc.training_program) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Training Program",
                    name: frm.doc.training_program
                },
                callback: function(r) {
                    if (r.message) {
                        let program = r.message;
                        frm.set_value("trainer_name", program.trainer_name);
                        frm.set_value("trainer_email", program.trainer_email);
                        frm.set_value("contact_number", program.contact_number);
                        frm.set_value("supplier", program.supplier);
                    }
                }
            });
        }
    }
});



// Function to show the training request dialog
function show_training_request_dialog(frm) {
    // Create a dialog to display training requests
    let dialog = new frappe.ui.Dialog({
        title: "Select Training Requests",
        fields: [
            {
                fieldname: "request_table",
                label: "Training Requests",
                fieldtype: "Table",
                cannot_add_rows: true,
                cannot_delete_rows: true,
                fields: [
                    {
                        fieldtype: "Data",
                        fieldname: "training_request_name",
                        label: "Request Name",
                        read_only: 1,
                        in_list_view: 1
                    },
                    {
                        fieldtype: "Link",
                        fieldname: "employee",
                        options: "Employee",
                        label: "Employee",
                        read_only: 1,
                        in_list_view: 1
                    },
                    {
                        fieldtype: "Data",
                        fieldname: "employee_name",
                        label: "Employee Name",
                        read_only: 1,
                        in_list_view: 1
                    }
                ]
            }
        ],
        primary_action_label: "Get Employees",
        primary_action(values) {
            var data = { request_table: dialog.fields_dict.request_table.grid.get_selected_children() };

            let selected_requests = [];

            // Loop through the rows in the table to check for the selected ones
            data.request_table.forEach(request => {
              selected_requests.push(request);
            });

            if (selected_requests.length === 0) {
                frappe.msgprint("No training requests selected.");
                return;
            }

            process_selected_requests(frm, selected_requests);
            dialog.hide();
        }
    });

    fetch_training_requests(frm, dialog);
    dialog.show();
}

// Function to fetch training requests using the custom server-side method
function fetch_training_requests(frm, dialog) {
    frappe.call({
        method: "beams.beams.custom_scripts.training_event.training_event.get_open_training_requests",
        callback: function(r) {
            if (r.message) {
                let rows = [];
                r.message.forEach(request => {
                    rows.push({
                        training_request_name: request.name,
                        employee: request.employee,
                        employee_name: request.employee_name,
                        selected: false
                    });
                });

                dialog.fields_dict.request_table.df.data = rows;
                dialog.fields_dict.request_table.refresh();
            } else {
                frappe.msgprint("No open training requests found.");
            }
        },
        error: function(r) {
            frappe.msgprint("Error fetching training requests. Please check your permissions.");
        }
    });
}

// Function to process selected training requests and add them to the Employees child table
function process_selected_requests(frm, selected_requests) {
    let existing_employees = frm.doc.employees.map(row => row.employee);

    selected_requests.forEach(request => {
        // Check if the employee is already in the child table
        if (!existing_employees.includes(request.employee)) {
            let row = frm.add_child("employees");
            row.employee = request.employee;
            row.employee_name = request.employee_name;
            row.training_request = request.training_request_name;
        }
    });

    frm.refresh_field("employees");
    frappe.msgprint("Selected employees have been added to the Training Event.");
}
