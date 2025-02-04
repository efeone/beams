// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Request', {
    refresh: function (frm) {
        set_item_query(frm)

        // Show the 'Asset Movement' button only if the document is submitted (docstatus == 1) and approved
        if (frm.doc.docstatus == 1 && frm.doc.workflow_state == 'Approved') {
            frm.add_custom_button(__('Asset Movement'), function () {
                let asset_movement = frappe.model.get_new_doc("Asset Movement");
                asset_movement.posting_date = frm.doc.posting_date; // Set posting date from the current document
                frappe.set_route("form", "Asset Movement", asset_movement.name); // Redirect to the new Asset Movement form
            }, __("Create"));
        }

        // Add a button to create an Equipment Acquiral Request
        frm.add_custom_button(__('Equipment Acquiral Request'), function () {
            frappe.model.open_mapped_doc({
                method: "beams.beams.doctype.equipment_request.equipment_request.map_equipment_acquiral_request",
                frm: frm,
            });
        }, __("Create"));
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
    }
});

frappe.ui.form.on('Required Items Detail', {
    required_item: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        frappe.call({
            method: "beams.beams.custom_scripts.project.project.get_available_quantities",
            args: {
                items: [row.required_item],
                bureau: frm.doc.bureau
            },
            callback: function(r) {
                if (r.message) {
                    const available_qty = r.message[row.required_item] || 0;
                    row.available_item_quantity = available_qty;
                    frm.refresh_field('required_equipments');
                }
            }
        });
    },
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
      // Fetch all assets with the same bureau
      frappe.call({
          method: 'frappe.client.get_list',
          args: {
              doctype: 'Asset',
              filters: {
                  bureau: frm.doc.bureau
              },
              fields: ['item_code'],
              limit_page_length: 0
          },
          callback: function (response) {
              if (response.message && response.message.length > 0) {
                  const item_codes = response.message.map(asset => asset.item_code);

                  // Set the filter for the child table's Required Item field
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
