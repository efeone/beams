// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

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
                            reqd: 1
                        },
                        {
                            fieldtype: 'Date',
                            label: 'Required by Date',
                            fieldname: 'schedule_date',
                            reqd: 1
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
                                qty: item.quantity
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
                            po.supplier = values.supplier;
                            po.schedule_date = values.schedule_date;

                            if (!po.supplier || !po.schedule_date) {
                                frappe.msgprint({
                                    title: __('Error'),
                                    indicator: 'red',
                                    message: __('Supplier and Required by Date are mandatory')
                                });
                                return;
                            }

                            values.items.forEach(item => {
                                let child = frappe.model.add_child(po, 'Purchase Order Item', 'items');
                                child.item_code = item.item_code;
                                child.qty = item.qty;
                                frm.doc.required_items.forEach(required_item => {
                                if (required_item.item === item.item_code) {
                                    child.reference_doctype = "Required Acquiral Items Detail";
                                    child.reference_document = required_item.name;
                                }
                            });
                            });
                            frappe.db.insert(po).then(doc => {
                                frappe.show_alert({
                                    message: __('Purchase Order created successfully'),
                                    indicator: 'green'
                                });
                                frappe.set_route('Form', 'Purchase Order', doc.name);
                                dialog.hide();
                            });
                        });
                    }
                });

                dialog.show();
            }, __('Create'));

            frm.add_custom_button(__('Service Purchase Order'), function() {
                let service_items = frm.doc.required_items.filter(item => item.is_service === 1);

                let dialog = new frappe.ui.Dialog({
                    title: __('Service Purchase Order'),
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
                            reqd: 1
                        },
                        {
                            fieldtype: 'Table',
                            label: 'Service Items',
                            fieldname: 'service_items',
                            fields: [
                                {
                                    fieldtype: 'Link',
                                    label: 'Service Item',
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
                                item_code: item.service_item,
                                qty: item.quantity
                            }))
                        }
                    ],
                    size: 'large',
                    primary_action_label: __('Create Service Purchase Order'),
                    primary_action: function() {
                        let values = dialog.get_values();

                        if (!values.supplier || !values.schedule_date) {
                            frappe.msgprint(__('Supplier and Required by Date are mandatory'));
                            return;
                        }

                        frappe.model.with_doctype('Purchase Order', function() {
                            let po = frappe.model.get_new_doc('Purchase Order');
                            po.supplier = values.supplier;
                            po.schedule_date = values.schedule_date;

                            values.service_items.forEach(service_item => {
                                let child = frappe.model.add_child(po, 'Purchase Order Item', 'items');
                                child.item_code = service_item.item_code;
                                child.qty = service_item.qty;
                                frm.doc.required_items.forEach(required_item => {
                                if (required_item.service_item === service_item.item_code) {
                                    child.reference_doctype = "Required Acquiral Items Detail";
                                    child.reference_document = required_item.name;
                                }
                            });
                            });

                            frappe.db.insert(po).then(doc => {
                                frappe.show_alert({
                                    message: __('Service Purchase Order created successfully'),
                                    indicator: 'green'
                                });
                                frappe.set_route('Form', 'Purchase Order', doc.name);
                                dialog.hide();
                            });
                        });
                    }
                });

                dialog.show();
            }, __('Create'));
        }
    },

    required_from(frm) {
        frm.call("validate_required_from_and_required_to");
    },

    required_to(frm) {
        frm.call("validate_required_from_and_required_to");
    },

    posting_date(frm) {
        frm.call("validate_posting_date");
    }
});
