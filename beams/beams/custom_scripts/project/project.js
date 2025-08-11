frappe.ui.form.on('Project', {
    refresh(frm) {

		//HIde Allocated Manpower Detail, Allocated Item Details, Allocated Vehicle Details
		let tables = [
			"allocated_manpower_details",
			"allocated_item_details",
			"allocated_vehicle_details"
		];

		tables.forEach(fieldname => {
			let grid = frm.fields_dict[fieldname].grid;
			grid.cannot_add_rows = true;
			grid.refresh();
		});

        // Hide Available Quantity , Return Date , Returned Count & Returned Reason in Allocated Item Details
        frm.fields_dict['allocated_item_details'].grid.toggle_display('available_quantity', false);
        frm.fields_dict['allocated_item_details'].grid.toggle_display('return_date', false);
        frm.fields_dict['allocated_item_details'].grid.toggle_display('returned_count', false);
        frm.fields_dict['allocated_item_details'].grid.toggle_display('returned_reason', false);

        // Hide Returned Date , Returned & Returned Reason in Allocated Manpower Details
        if (frm.fields_dict["allocated_manpower_details"] && frm.fields_dict["allocated_manpower_details"].grid) {
            let grid = frm.fields_dict["allocated_manpower_details"].grid;
            grid.toggle_display("returned_date", false);
            grid.toggle_display("returned", false);
            grid.toggle_display("returned_reason", false);
            frm.refresh_field("allocated_manpower_details");
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

        //function adds Equipment Request button under Create.
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
                            items: JSON.stringify([row.item]),
                            source_name: frm.doc.name
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

          //  Pre-fill from required_items table if available
          const required_items = frm.doc.required_items || [];
          if (required_items.length) {
            const item_codes = required_items.map(d => d.required_item);
            frappe.call({
              method: "beams.beams.custom_scripts.project.project.get_available_quantities",
              args: {
                items: JSON.stringify(item_codes),
                source_name: frm.doc.name
              },
              callback: function (r) {
                const qty_map = r.message || {};
                const rows = required_items.map(d => ({
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
      },

      return: function(frm, cdt, cdn) {
          let child = locals[cdt][cdn];

          frappe.prompt([
              {
                  label: 'Returned Date',
                  fieldname: 'returned_date',
                  fieldtype: 'Datetime',
                  reqd: 1
              },
              {
                  label: 'Returned Reason',
                  fieldname: 'returned_reason',
                  fieldtype: 'Small Text',
                  reqd: 1
              }
          ],
          function(values) {
              frappe.model.set_value(cdt, cdn, 'returned_date', values.returned_date);
              frappe.model.set_value(cdt, cdn, 'returned_reason', values.returned_reason);
              frappe.model.set_value(cdt, cdn, 'returned', 1);

              let args = {
                  project: frm.doc.name,
                  assigned_from: child.assigned_from,
                  returned_date: values.returned_date,
                  returned_reason: values.returned_reason
              };

              if (child.employee) {
                  args.employee = child.employee;
              } else if (child.hired_personnel) {
                  args.hired_personnel = child.hired_personnel;
              }

              frappe.call({
                  method: "beams.beams.custom_scripts.project.project.update_return_details_in_log",
                  args: args,
                  callback: function(r) {
                      if (!r.exc) {
                          frappe.msgprint("Manpower Transaction Log updated.");
                      }
                  }
              });
          },
          'Return Manpower',
          'Submit');
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


  frappe.ui.form.on('Required Items Table', {
    required_item: function(frm, cdt, cdn) {
      let row = locals[cdt][cdn];
      if (row.required_item) {
        frappe.call({
          method: "beams.beams.custom_scripts.project.project.get_available_quantities",
          args: {
            items: JSON.stringify([row.required_item]),
            source_name: frm.doc.name
          },
          callback: function(r) {
            if (r.message) {
              if (r.message._error) {
                frappe.model.set_value(cdt, cdn, 'available_quantity', 0);
              } else {
                frappe.model.set_value(cdt, cdn, 'available_quantity', r.message[row.required_item] || 0);
              }
            }
          }
        });
      }
    }
  });

  frappe.ui.form.on('Allocated Vehicle Details', {
      return: function(frm, cdt, cdn) {
          let row = locals[cdt][cdn];
          frappe.prompt([
              {
                  label: 'Return Date',
                  fieldname: 'return_date',
                  fieldtype: 'Datetime',
                  reqd: 1
              },
              {
                  label: 'Return Reason',
                  fieldname: 'return_reason',
                  fieldtype: 'Small Text',
                  reqd: 1
              }
          ],
          function(values) {
              row.return_date = values.return_date;
              row.return_reason = values.return_reason;
              row.returned = 1;
              frm.refresh_field('allocated_vehicle_details');
              frappe.call({
                  method: "beams.beams.custom_scripts.project.project.update_vehicle_return_details_in_log",
                  args: {
                      project: frm.doc.name,
                      vehicle: row.vehicle,
                      return_date: values.return_date,
                      return_reason: values.return_reason
                  },
                  callback: function(r) {
                      if (!r.exc) {
                          frappe.msgprint("Vehicle Transaction Log updated.");
                          frm.save();
                      }
                  }
              });
          },
          'Return Vehicle',
          'Submit');
      }
  });

  frappe.ui.form.on('Required Items Detail', {
      return: function(frm, cdt, cdn) {
          let child = locals[cdt][cdn];

          frappe.prompt([
              {
                  label: 'Return Date',
                  fieldname: 'return_date',
                  fieldtype: 'Datetime',
                  reqd: 1
              },
              {
                  label: 'Returned Reason',
                  fieldname: 'returned_reason',
                  fieldtype: 'Small Text',
                  reqd: 1
              },
              {
                label: 'Returned Count',
                fieldname: 'returned_count',
                fieldtype: 'Int',
                reqd: 1
            }
          ],
          function(values) {
              frappe.model.set_value(cdt, cdn, 'return_date', values.return_date);
              frappe.model.set_value(cdt, cdn, 'returned_reason', values.returned_reason);
              frappe.model.set_value(cdt, cdn, 'returned_count', values.returned_count);

              let args = {
                  project: frm.doc.name,
                  required_item: child.required_item,
                  return_date: values.return_date,
                  returned_reason: values.returned_reason,
                  returned_count: values.returned_count
              };

              frappe.call({
                  method: "beams.beams.custom_scripts.project.project.update_return_details_in_equipment_log",
                  args: args,
                  callback: function(r) {
                      if (!r.exc) {
                          frappe.msgprint("Equipment Transaction Log updated successfully.");
                      }
                  }
              });
          },
          'Return Equipment',
          'Submit');
      }
  });
