// // // Copyright (c) 2025, efeone and contributors
// // // For license information, please see license.txt


frappe.ui.form.on('Asset Request', {
    refresh: function(frm) {
        frm.add_custom_button(__('Assign Assets'), function() {
            open_assign_assets_popup(frm);
        }, __("Actions")); 
    }
});

function open_assign_assets_popup(frm) {
    let rows = [];
    (frm.doc.items || []).forEach(item => {
        let qty = item.required_quantity || 0;
        for (let i = 0; i < qty; i++) {
            rows.push({
                item: item.item_code || "",
                item_type: item.item_type || "",
                asset_type: item.asset_type || ""
            });
        }
    });

    let d = new frappe.ui.Dialog({
        title: __('Assign Assets'),
        fields: [
            {
                label: 'Assigned To',
                fieldname: 'assigned_to',
                fieldtype: 'Link',
                options: 'Employee',
                reqd: 1
            },
            {
                label: __("Purpose"),
                fieldname: "purpose",
                fieldtype: "Select",
                options: ["Issue", "Transfer", "Receipt", "Return"],
                default: "Issue",
                reqd: 1
            },
            {
                label: 'Items',
                fieldname: 'items_table',
                fieldtype: 'Table',
                cannot_add_rows: false,
                in_place_edit: true,
                data: rows,
                fields: [
                    { label: 'Item', fieldname: 'item', fieldtype: 'Link', options: 'Item', in_list_view: 1 },
                    { label: 'Asset Type', fieldname: 'asset_type', fieldtype: 'Select', options: '\nSingle Asset\nBundle', in_list_view: 1 },
                    { label: 'Asset', fieldname: 'asset', fieldtype: 'Link', options: 'Asset', in_list_view: 1 },
                    { label: 'Bundle', fieldname: 'bundle', fieldtype: 'Link', options: 'Asset Bundle', in_list_view: 1 }
                ]
            }
        ],
        primary_action_label: __('Assign'),
        primary_action(values) {
            frappe.call({
                method: "beams.beams.doctype.asset_request.asset_request.create_asset_movement",
                args: {
                    assigned_to: values.assigned_to,
                    purpose: values.purpose,
                    items: values.items_table,
                    reference_name: frm.doc.name
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.set_route("Form", "Asset Movement", r.message.name);
                        d.hide();
                    }
                }
            });
        }
    });

    d.show();

    // filter Asset field by selected Item
    d.fields_dict.items_table.grid.get_field('asset').get_query = function(doc, cdt, cdn) {
        let row = locals[cdt] && locals[cdt][cdn];
        if (row && row.item) {
            return {
                filters: { item_code: row.item }
            };
        }
        return {};
    };
}


