frappe.ui.form.on('Project', {
    refresh(frm) {
      //function adds a button to the 'Project' form to create an Adhoc Budget.
        frm.add_custom_button(__('Adhoc Budget'), function () {
            frappe.model.open_mapped_doc({
                method: "beams.beams.custom_scripts.project.project.create_adhoc_budget",
                frm: frm,
            });
        }, __("Create"));

        // Add a button to create an Equipment Hire Request
        frm.add_custom_button(__('Equipment Hire Request'), function () {
            frappe.model.open_mapped_doc({
                method: "beams.beams.custom_scripts.project.project.create_equipment_hire_request",
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


      // Add "Technical Request" button under the "Create" group
      frm.add_custom_button(__('Technical Request'), function () {
          // Open a dialog with the specified fields
          let dialog = new frappe.ui.Dialog({
              title: 'Technical Request',
              fields: [
                  {
                      fieldtype: 'Table',
                      label: 'Requirements',
                      fieldname: 'requirements',
                      reqd: 1,
                      fields: [
                          {
                              label: 'Department',
                              fieldtype: 'Link',
                              fieldname: 'department',
                              options: 'Department',
                              in_list_view: 1,
                              reqd: 1
                          },
                          {
                              label: 'Designation',
                              fieldtype: 'Link',
                              fieldname: 'designation',
                              options: 'Designation',
                              in_list_view: 1,
                              reqd: 1
                          },
                          {
                              label: 'Required From',
                              fieldtype: 'Datetime',
                              fieldname: 'required_from',
                              in_list_view: 1,
                              reqd: 1
                          },
                          {
                              label: 'Required To',
                              fieldtype: 'Datetime',
                              fieldname: 'required_to',
                              in_list_view: 1,
                              reqd: 1
                          },
                          {
                              label: 'Remarks',
                              fieldtype: 'Small Text',
                              fieldname: 'remarks',
                              in_list_view: 1
                          }
                      ]
                  }
              ],
              size: 'large',
              primary_action_label: 'Submit',
              primary_action: function () {
                  let values = dialog.get_values();
                  if (values && values.requirements) {
                      // Perform validation for each row
                      for (let i = 0; i < values.requirements.length; i++) {
                          let row = values.requirements[i];

                          if (!row.required_from || !row.required_to) {
                              frappe.msgprint({
                                  title: __('Validation Error'),
                                  message: __('Please fill both "Required From" and "Required To" in #row  {0}.', [i + 1]),
                                  indicator: 'red'
                              });
                              return;
                          }

                          // Ensure Required To is later than Required From
                          if (row.required_to <= row.required_from) {
                              frappe.msgprint({
                                  title: __('Validation Error'),
                                  message: __('"Required To" must be later than "Required From" in # row {0}.', [i + 1]),
                                  indicator: 'red'
                              });
                              return;
                          }
                      }

                      frappe.call({
                          method: 'beams.beams.custom_scripts.project.project.create_technical_support_request',
                          args: {
                              project_id: frm.doc.name,
                              requirements: JSON.stringify(values.requirements)
                          },
                      });
                      dialog.hide();
                  }
              }
          });
          dialog.show();
        }, __("Create"));
     }
  });

frappe.ui.form.on('Project', {
    refresh: function(frm) {
      console.log("in refresh")
        frm.fields_dict['allocated_resources_details'].grid.get_field('employee').get_query = function(doc, cdt, cdn) {
            let allocated_employees = [];
            let row = locals[cdt][cdn]

            // Check if the child table is populated
            if (doc.allocated_resources_details) {
                console.log("Allocated Resources Details: ", doc.allocated_resources_details); // Log the child table data

                doc.allocated_resources_details.forEach(function(d) {
                    if (d.employee && d.assigned_from && d.assigned_to) {
                        let assigned_from = d.assigned_from;
                        let assigned_to = d.assigned_to;

                        // Log to ensure the dates are captured correctly
                        console.log("Employee: ", d.employee, " Assigned From: ", assigned_from, " Assigned To: ", assigned_to);

                        // Ensure dates are in the correct format (just focusing on comparison)
                        if (assigned_from && assigned_to && (assigned_from <= assigned_to)) {
                            allocated_employees.push(d.employee);  // Push the employee to exclude them from the list
                        }
                    }
                });
            }

            frappe.call('beams.beams.custom_scripts.project.project.get_assigned_resources', {
            cur_project: frm.doc.name,
             assigned_from: row.assigned_from,
             assigned_to: row.assigned_to
            }).then(r => {
              r.message.forEach((item) => {
                allocated_employees.push(item)
                console.log("in py loop")
                console.log(item)
              });

            })


            // Log the list of allocated employees to ensure they are being captured
            console.log("Allocated Employees: ", allocated_employees);
            console.log(typeof(allocated_employees))

            // Return the query with the filter to exclude already allocated employees
            return {
                filters: {
                    'name': ['not in', allocated_employees],  // Exclude employees already allocated in other projects
                    // Additional filter can be applied for other criteria like project status or designation if needed
                }
            };
        };
    }
});
