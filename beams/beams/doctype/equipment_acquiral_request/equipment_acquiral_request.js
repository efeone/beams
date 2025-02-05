frappe.ui.form.on("Equipment Acquiral Request", {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.workflow_state === 'Approved') {
            frm.add_custom_button(__('Purchase Order'), function() {
                let dialog = new frappe.ui.Dialog({
                    title: __('Purchase Order'),
                    fields: [
                        {
                            fieldtype: 'Link',
                            label: 'Supplier',
                            fieldname: 'supplier',
                            options: 'Supplier',
                            reqd: 1,
                            in_list_view: 1
                        },
                        {
                            fieldtype: 'Date',
                            label: 'Required by Date',
                            fieldname: 'schedule_date',
                            reqd: 1,
                            in_list_view: 1
                        },
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
                                    fieldtype: 'Float',
                                    label: 'Quantity',
                                    fieldname: 'qty',
                                    in_list_view: 1
                                }
                            ],
                            data: frm.doc.required_items.map(item => ({
                                item_code: item.item,
                                qty: item.quantity,
                                acquired_qty: item.acquired_qty || 0
                            }))
                        }
                    ],
                    size: 'large',
                    primary_action_label: __('Create Purchase Order'),
                    primary_action: function() {
                        let values = dialog.get_values();
                        frappe.model.with_doctype('Purchase Order', function() {
                            let po = frappe.model.get_new_doc('Purchase Order');

                            po.posting_date = frm.doc.posting_date;

                            values.items.forEach(item => {
                                let child = frappe.model.add_child(po, 'Purchase Order Item', 'items');
                                child.item_code = item.item_code;
                                child.qty = item.qty;
                                child.acquired_qty = item.acquired_qty;
                            });

                            po.supplier = values.supplier;

                            if (!po.supplier) {
                                frappe.msgprint({
                                    title: __('Error'),
                                    indicator: 'red',
                                    message: __('Please select a supplier')
                                });
                                return;
                            }

                            po.schedule_date = values.schedule_date;

                            if (!po.schedule_date) {
                                frappe.msgprint({
                                    title: __('Error'),
                                    indicator: 'red',
                                    message: __('Please select a Required by Date')
                                });
                                return;
                            }

                            frappe.db.insert(po)
                                .then(doc => {
                                    frappe.show_alert({
                                        message: __('Purchase Order created'),
                                        indicator: 'green'
                                    });
                                    frappe.set_route('Form', 'Purchase Order', doc.name);
                                    dialog.hide();
                                })
                        });
                    }
                });

                dialog.show();
            }, __('Create'));
        }
    },

    required_from: function (frm) {
        frm.call("validate_required_from_and_required_to");
    },

    required_to: function (frm) {
        frm.call("validate_required_from_and_required_to");
    },

    posting_date: function (frm) {
        frm.call("validate_posting_date");
    }
});
