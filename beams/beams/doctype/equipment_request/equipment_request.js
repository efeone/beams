// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Request', {
    refresh: function (frm) {
        if (frm.doc.workflow_state === "Approved") {
            frm.add_custom_button(__('Equipment Acquiral Request'), function () {
                frappe.model.open_mapped_doc({
                    method: "beams.beams.doctype.equipment_request.equipment_request.map_equipment_acquiral_request",
                    frm: frm,
                });
            }, __("Create"));

            frm.add_custom_button(__('Asset Movement'), function () {
                const default_items = (frm.doc.required_equipments || []).map(row => ({
                    item: row.required_item,
                    count: row.required_quantity
                }));

                const fields = [
                    {
                        label: 'Assigned To',
                        fieldname: 'assigned_to',
                        fieldtype: 'Link',
                        options: 'User',
                        reqd: 1,
                        default: frm.doc.requested_by || frappe.session.user 
                    },
                    {
                        fieldname: 'asset_movement_details',
                        label: 'Asset Movement Details',
                        fieldtype: 'Table',
                        cannot_add_rows: false,
                        reqd: 1,
                        fields: [
                            {
                                label: 'Item',
                                fieldname: 'item',
                                fieldtype: 'Link',
                                options: 'Item',
                                in_list_view: 1,
                                reqd: 1
                            },
                            {
                                label: 'Count',
                                fieldname: 'count',
                                fieldtype: 'Int',
                                in_list_view: 1,
                                reqd: 1
                            }
                        ],
                        data: default_items
                    }
                ];

                frappe.prompt(fields, function (values) {
                    frappe.call({
                        method: "beams.beams.doctype.equipment_request.equipment_request.map_asset_movement",
                        args: {
                            source_name: frm.doc.name,
                            assigned_to: values.assigned_to,
                            items: values.asset_movement_details,
                            purpose: "Transfer"
                        },
                        callback: function (r) {
                            if (r.message) {
                                r.message.purpose = "Issue";
                                frappe.model.sync(r.message);
                                frappe.set_route('Form', r.message.doctype, r.message.name);
                            }
                        }
                    });
                }, __('Asset Movement'), __('Submit'));
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
    form_render: function(frm, cdt, cdn) {
        if (frm.doc.workflow_state != "Approved") {
            $(".btn.btn-xs.btn-default").hide();
        }
    },
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
