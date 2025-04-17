// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("External Resource Request", {
      required_from: function (frm) {
          frm.call('updated_required_resources',)
          .then(r => {
              if (r.message) {
                  frm.refresh_field("required_resources");
              }
          })
      },

      required_to: function (frm) {
        frm.call('updated_required_resources',)
        .then(r => {
            if (r.message) {
                frm.refresh_field("required_resources");
            }
        })
      },
        refresh: function (frm) {
            if (!frm.is_new()) {
                frm.add_custom_button(__('Service Purchase Order'), function () {
                    let dialog = new frappe.ui.Dialog({
                        title: __('Create Service Purchase Order'),
                        fields: [
                            {
                                fieldtype: 'Link',
                                label: 'Supplier',
                                fieldname: 'supplier',
                                options: 'Supplier',
                                reqd: 1
                            },
                            {
                                fieldtype: 'Date',
                                label: 'Required by Date',
                                fieldname: 'schedule_date',
                                default: frappe.datetime.nowdate(),
                                reqd: 1
                            },
                            {
                                fieldtype: 'Link',
                                label: 'Service Item',
                                fieldname: 'service_item',
                                options: 'Item',
                                reqd: 1,
                                get_query: function () {
                                    return {
                                        filters: {
                                            hireable: 1
                                        }
                                    };
                                }
                            },
                            {
                                fieldtype: 'Float',
                                label: 'Quantity',
                                fieldname: 'qty',
                                default: 1,
                                reqd: 1
                            },
                            {
                                fieldtype: 'Currency',
                                label: 'Rate',
                                fieldname: 'rate',
                                reqd: 1
                            }
                        ],
                        primary_action_label: __('Create Purchase Order'),
                        primary_action: function () {
                            let values = dialog.get_values();

                            if (!values.supplier || !values.schedule_date || !values.service_item || !values.qty || !values.rate) {
                                frappe.msgprint(__('All fields are required!'));
                                return;
                            }

                            frappe.call({
                                method: "frappe.client.insert",
                                args: {
                                    doc: {
                                        doctype: "Purchase Order",
                                        supplier: values.supplier,
                                        transaction_date: frappe.datetime.nowdate(),
                                        schedule_date: values.schedule_date,
                                        items: [
                                            {
                                                item_code: values.service_item,
                                                qty: values.qty,
                                                rate: values.rate,
                                                amount: values.qty * values.rate,
                                                uom: "Nos"
                                            }
                                        ]
                                    }
                                },
                                callback: function (response) {
                                    if (response.message) {
                                        frappe.set_route('Form', 'Purchase Order', response.message.name);
                                    }
                                }
                            });

                            dialog.hide();
                        }
                    });

                    dialog.show();
                }, __("Create"));
            }
        }
    });


    frappe.ui.form.on("External Resources Detail", {
        required_resources_add: function (frm, cdt, cdn) {
          frm.call('updated_required_resources',)
          .then(r => {
              if (r.message) {
                  frm.refresh_field("required_resources");
              }
          })
        },

        designation: function (frm, cdt, cdn) {
          let row = locals[cdt][cdn];
          if (row.designation) {
            frm.fields_dict.required_resources.grid.update_docfield_property(
                "hired_personnel",
                "get_query",
                function () {
                    return {
                        filters: {
                            designation: row.designation
                        }
                    };
                }
            );
          
            frappe.model.set_value(cdt, cdn, "hired_personnel", null);
          } else {
            frm.fields_dict.required_resources.grid.update_docfield_property(
                "hired_personnel",
                "get_query",
                null
            );
        }
      }
    });
