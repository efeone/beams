// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Request', {
    refresh: function (frm) {
        set_item_query(frm)
        if (frm.doc.workflow_state === "Approved"){
          frm.add_custom_button(__('Equipment Acquiral Request'), function () {
              frappe.model.open_mapped_doc({
                  method: "beams.beams.doctype.equipment_request.equipment_request.map_equipment_acquiral_request",
                  frm: frm,
              });
          }, __("Create"));
        }
    },

    bureau: function (frm) {
        set_item_query(frm)
    },
    required_from: function (frm) {
        frm.call("validate_required_from_and_required_to");
    },
    required_to: function (frm) {
        frm.call("validate_required_from_and_required_to");
    },
    posting_date:function (frm){
      frm.call("validate_posting_date");
    },
    location: function(frm) {
      frm.clear_table("required_equipments");
    }
});

frappe.ui.form.on('Required Items Detail', {
    required_item: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!frm.doc.location) {
            frappe.msgprint(__('Please select a location first.'));
            return;
        }
        frappe.call({
            method: "beams.beams.custom_scripts.project.project.get_available_quantities",
            args: {
                items: [row.required_item],
                location: frm.doc.location
            },
            callback: function(r) {
                if (r.message) {
                    const available_qty = r.message[row.required_item] || 0;
                    row.available_quantity = available_qty;
                    frm.refresh_field('required_equipments');
                }
            }
        });
    },

    asset_movement: function (frm, cdt, cdn) {
       let row = locals[cdt][cdn];
       frappe.db.get_value('Item', row.required_item, 'item_code', function(r) {
           if (r && r.item_code) {
               // Open the prompt dialog with employee and asset fields
               frappe.prompt([
                   {
                       label: 'Employee',
                       fieldname: 'employee',
                       fieldtype: 'Link',
                       options: 'Employee',
                       reqd: 1
                   },
                   {
                       label: 'Asset',
                       fieldname: 'asset',
                       fieldtype: 'Link',
                       options: 'Asset',
                       reqd: 1,
                       get_query: function () {
                           return {
                               filters: { item_code: r.item_code }  // Filter assets by item_code
                           };
                       }
                   }
               ],
               function(values) {
                   // Call backend method to map the asset movement
                   frappe.model.open_mapped_doc({
                       method: "beams.beams.doctype.equipment_request.equipment_request.map_asset_movement",
                       frm: frm,
                       args: {
                         to_employee: values.employee,
           							 asset: values.asset
           						}
                   });
               }, __('Asset Movement'), __('Create'));
           } else {
               frappe.msgprint(__('Invalid required item selected.'));
           }
       });
      }
    });

function validate_dates(frm) {
    if (frm.doc.required_from && frm.doc.required_to) {
        if (frm.doc.required_from > frm.doc.required_to) {
            frappe.throw(__('The "Required From" date cannot be after the "Required To" date.'));
        }
    }
}

function set_item_query(frm) {
  if (frm.doc.bureau) {
      frappe.call({
          method: 'frappe.client.get_list',
          args: {
              doctype: 'Asset',
              filters: {
                  location: frm.doc.location
              },
              fields: ['item_code'],
              limit_page_length: 0
          },
          callback: function (response) {
              if (response.message && response.message.length > 0) {
                  const item_codes = response.message.map(asset => asset.item_code);

                  frm.fields_dict['required_equipments'].grid.get_field('required_item').get_query = function () {
                      return {
                          filters: {
                              name: ['in', item_codes]
                          }
                      };
                  };
              }
          }
      });
  }
}
