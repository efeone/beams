// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Acquiral Request", {
    refresh(frm) {
        // Show the 'Purchase Invoice' button only if the document is submitted (docstatus == 1) and approved
        if (frm.doc.docstatus == 1 && frm.doc.workflow_state == 'Approved') {

            // Create 'Purchase Invoice' button
            frm.add_custom_button(__('Purchase Order'), function () {
              let dialog = new frappe.ui.Dialog({
                  title: __('Purchase Order'),
                  fields: [
                      {
                          fieldtype: 'Table',
                          label: 'Items',
                          fieldname: 'items',
                          reqd: 1,
                          fields: [
                              {
                                  fieldtype: 'Link',
                                  label: 'Item',
                                  fieldname: 'item_code',
                                  options: 'Item',
                                  in_list_view: 1
                              },
                              {
                                  fieldtype: 'Data',
                                  label: 'Quantity',
                                  fieldname: 'qty',
                                  in_list_view: 1
                              },
                              {
                                  fieldtype: 'Int',
                                  label: 'Acquired Quandity',
                                  fieldname: 'acquired_qty',
                                  in_list_view: 1
                              }
                          ],
                          data: frm.doc.required_items.map(item => {
                              return {
                                  item_code: item.item,
                                  qty: item.quantity,
                                  acquired_qty:item.acquired_qty
                              };
                          })
                      }
                  ],
                  size: 'large',
                  primary_action_label: __('Create Purchase Order'),
                  primary_action: function () {
                    let items = dialog.get_values().items;
                    let po = frappe.model.get_new_doc("Purchase Order");
                    po.posting_date = frm.doc.posting_date;
                    items.forEach(item => {
                        po.items.push({
                            item_code: item.item_code,
                            qty: item.qty,
                            acquired_qty: item.acquired_qty
                        });
                    });
                    frappe.db.insert(po).then(doc => {
                        frappe.set_route("form", "Purchase Order", doc.name);
                        dialog.hide();
                    })
                }
                  });
            dialog.show();
            }, __("Create"));

            // Create 'Asset Movement' button
            frm.add_custom_button(__('Asset Movement'), function () {
                let asset_movement = frappe.model.get_new_doc("Asset Movement");
                asset_movement.posting_date = frm.doc.posting_date; // Set posting date from the current document
                frappe.set_route("form", "Asset Movement", asset_movement.name); // Redirect to the new Asset Movement form
            }, __("Create"));
        }
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
});
