frappe.ui.form.on('Project', {
    refresh(frm) {

        // Hide Asset Movement in Allocated Item Details
        if (frm.fields_dict["allocated_item_details"] && frm.fields_dict["allocated_item_details"].grid) {
            let grid = frm.fields_dict["allocated_item_details"].grid;
            grid.toggle_display("asset_movement", false);
            frm.refresh_field("allocated_item_details");
        }

      //function adds a button to the 'Project' form to create an Adhoc Budget.
        frm.add_custom_button(__('Adhoc Budget'), function () {
            frappe.model.open_mapped_doc({
                method: "beams.beams.custom_scripts.project.project.create_adhoc_budget",
                frm: frm,
            });
        }, __("Create"));


        frm.add_custom_button(__('Technical Request'), function () {
         frappe.call({
             method: "beams.beams.custom_scripts.project.project.create_technical_request",
             args: {
                 project_id: frm.doc.name
             },
             callback: function (r) {
                 if (r.message) {
                     frappe.set_route("Form", "Technical Request", r.message);
                 }
             }
         });
     }, __("Create"));


        frm.add_custom_button(__('Equipment Request'), function () {
            const dialog = new frappe.ui.Dialog({
              title: 'Equipments',
              fields: [
                {
                  label: 'Required From',
                  fieldtype: 'Datetime',
                  fieldname: 'required_from',
                  default: frm.doc.expected_start_date || frappe.datetime.now_datetime(),
                  reqd: 1
                },
                {
                  label: 'Required To',
                  fieldtype: 'Datetime',
                  fieldname: 'required_to',
                  default: frm.doc.expected_end_date || frappe.datetime.now_datetime(),
                  reqd: 1
                },
                {
                  fieldtype: 'Table',
                  label: 'Equipments',
                  fieldname: 'equipments',
                  reqd: 1,
                  fields: [
                    {
                      label: 'Item',
                      fieldtype: 'Link',
                      fieldname: 'item',
                      options: 'Item',
                      in_list_view: 1,
                      reqd: 1,
                      onchange: function (frm, cdt, cdn) {
                        let row = frappe.get_doc(cdt, cdn);
                        if (row.item) {
                          frappe.call({
                            method: "beams.beams.custom_scripts.project.project.get_available_quantities",
                            args: {
                              items: JSON.stringify([row.item])
                            },
                            callback: function (r) {
                              if (r.message) {
                                row.available_quantity = r.message[row.item];
                                dialog.fields_dict.equipments.grid.refresh();
                              }
                            }
                          });
                        }
                      }
                    },
                    {
                      label: 'Available Quantity',
                      fieldtype: 'Int',
                      fieldname: 'available_quantity',
                      in_list_view: 1,
                      read_only: 1,
                      default: 0
                    },
                    {
                      label: 'Required Quantity',
                      fieldtype: 'Int',
                      fieldname: 'required_quantity',
                      in_list_view: 1,
                      reqd: 1
                    }
                  ]
                }
              ],
              size: 'large',
              primary_action_label: 'Submit',
              primary_action(values) {
                const equipment_data = values?.equipments || [];
          
                if (!values.required_from || !values.required_to) {
                  frappe.msgprint(__('Both "Required From" and "Required To" are mandatory.'));
                  return;
                }
          
                if (values.required_from >= values.required_to) {
                  frappe.msgprint(__('"Required From" date should be earlier than "Required To" date.'));
                  return;
                }
          
                if (!equipment_data.length) {
                  frappe.msgprint(__('Please add at least one equipment row.'));
                  return;
                }
          
                const request_data = equipment_data.map(row => ({
                  item: row.item,
                  required_quantity: row.required_quantity,
                  available_quantity: row.available_quantity,
                  required_from: values.required_from,
                  required_to: values.required_to
                }));
          
                frappe.call({
                  method: 'beams.beams.custom_scripts.project.project.create_equipment_request',
                  args: {
                    source_name: frm.doc.name,
                    equipment_data: JSON.stringify(request_data),
                    required_from: values.required_from,
                    required_to: values.required_to
                  }
                }).then(() => {
                  dialog.hide();
                  frm.reload_doc();
                });
              }
            });
          
            // Pre-populate from required_items if present
            let required_items = frm.doc.required_items || [];
            if (required_items.length) {
              let item_codes = required_items.map(d => d.required_item);
              frappe.call({
                method: "beams.beams.custom_scripts.project.project.get_available_quantities",
                args: {
                  items: JSON.stringify(item_codes)
                },
                callback: function (r) {
                  let qty_map = r.message || {};
                  let rows = required_items.map(d => ({
                    item: d.required_item,
                    available_quantity: qty_map[d.required_item] || 0,
                    required_quantity: d.required_quantity || 1
                  }));
          
                  dialog.fields_dict.equipments.df.data = rows;
                  dialog.fields_dict.equipments.grid.refresh();
                }
              });
            }
          
            dialog.show();
          }, __("Create"));
          
        frm.add_custom_button("External Resource Request", function() {
            frappe.new_doc("External Resource Request", {
                project: frm.doc.name,
                bureau: frm.doc.bureau
            });
        }, "Create");
        // Adds a button to the 'Project' form to create an Transportation Request.
        frm.add_custom_button(__('Transportation Request'), function () {
            frappe.model.open_mapped_doc({
                method: "beams.beams.custom_scripts.project.project.create_transportation_request",
                frm: frm,
            });
        }, __("Create"));
        // Ensure filtering is applied when form loads
        frm.fields_dict.allocated_manpower_details.grid.get_field("employee").get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                filters: {
                    designation: row.designation || ""
                }
            };
        };
      },
      
    required_from : function(frm) {
       frm.doc.required_manpower_details.forEach(row => {
           if (row.required_from < row.required_to) {
               frappe.throw(__('Required To must be greater than Required From date in row {0}', [row.idx]));
           }
       });
   }
    });


    // Apply filter dynamically when Designation field changes in child table
  frappe.ui.form.on('Allocated Manpower Detail', {
      designation: function(frm, cdt, cdn) {
          let row = locals[cdt][cdn];
          frappe.model.set_value(cdt, cdn, 'employee', '');
          if (row.designation) {
              frm.fields_dict.allocated_manpower_details.grid.get_field("employee").get_query = function(doc, cdt, cdn) {
                  let child_row = locals[cdt][cdn];
                  return {
                      filters: {
                          designation: child_row.designation
                      }
                  };
              };
          }
          frm.refresh_field("allocated_manpower_details");
      }
  });
  frappe.ui.form.on('Required Manpower Details', {
      required_to: function(frm, cdt, cdn) {
          validate_dates(cdt, cdn);
      }
  });

  function validate_dates(cdt, cdn) {
      let row = locals[cdt][cdn];
      if (row.required_from && row.required_to && row.required_from > row.required_to) {
          frappe.msgprint(`Row ${row.idx || ''}: "Required From" must be before "Required To"`);
      }
  }


frappe.ui.form.on('Required Items Detail', {
  required_item: function(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.required_item) {
      frappe.call({
        method: "beams.beams.custom_scripts.project.project.get_available_quantities",
        args: {
          items: JSON.stringify([row.required_item])
        },
        callback: function (r) {
          if (r.message) {
            frappe.model.set_value(cdt, cdn, 'available_quantity', r.message[row.required_item] || 0);
          }
        }
      });
    }
  }
});