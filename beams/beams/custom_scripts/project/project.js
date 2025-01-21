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


      // Add "Technical Support Request" button under the "Create" group
      frm.add_custom_button(__('Technical Support Request'), function () {
          // Open a dialog with the specified fields
          let dialog = new frappe.ui.Dialog({
              title: 'Technical Support Request',
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
