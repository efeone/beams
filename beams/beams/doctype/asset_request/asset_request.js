// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Request', {
    onload_post_render: function(frm) {
        make_child_table_read_only(frm);
    },
    refresh: function(frm) {
        if (frm.doc.workflow_state === "Approved by Asset Manager" &&
            (frappe.user_roles.includes("Asset Manager") || frappe.user_roles.includes("Asset User"))) {
            frm.add_custom_button(__('Assign Assets'), function() {
                open_assign_assets_popup(frm);
            }, __("Create"));
        }

        make_child_table_read_only(frm);
        asset_recevied_acknowledgement(frm);
    }
});

function make_child_table_read_only(frm) {

    if (frm.doc.workflow_state == "Draft") {
        ['asset_type', 'item_code', 'issued_quantity', 'acquired_quantity'].forEach(field => {
            frm.fields_dict.items.grid.update_docfield_property(field, "read_only", 1);
        });
    }

    frm.fields_dict['items'].grid.refresh();
}


/**
 * Opens a dialog to assign assets based on the Asset Request form.
 */
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
                reqd: 1,
                default: frm.doc.requested_by
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
                        frappe.msgprint(__('Asset Movement {0} created and submitted', [r.message.name]));
                        d.hide();
                    }
                }
            });
        }
    });

    d.show();

    const table = d.fields_dict.items_table.grid;

    // Filter Assets per row dynamically
    table.get_field('asset').get_query = function(doc, cdt, cdn) {
        let row = table.grid_rows_by_docname[cdn].doc;

        // Already selected assets for the same item
        let selected_assets = table.get_data()
            .filter(r => r.item === row.item && r.asset && r.name !== row.name)
            .map(r => r.asset);

        return {
            filters: [
                ['item_code', '=', row.item || ''],
                ['custodian', 'is', 'not set'],
                ['docstatus', '=', 1],
                ['name', 'not in', selected_assets]
            ]
        };
    };

    // Filter Bundles per row dynamically
    table.get_field('bundle').get_query = function(doc, cdt, cdn) {
        let row = table.grid_rows_by_docname[cdn].doc;

        // Already selected bundles for the same item
        let selected_bundles = table.get_data()
            .filter(r => r.item === row.item && r.bundle && r.name !== row.name)
            .map(r => r.bundle);

        return {
            filters: [
                ['parent_item', '=', row.item || ''],
                ['name', 'not in', selected_bundles]
            ]
        };
    };

    // Refresh table when asset or bundle is changed to update dropdowns live
    table.wrapper.on('change', 'input[data-fieldname="asset"], input[data-fieldname="bundle"], input[data-fieldname="item"]', function() {
        table.refresh();
    });
}


function asset_recevied_acknowledgement(frm) {

    const has_unacknowledged = (frm.doc.allocated_assets || []).some(row => !row.acknowledged);
    if (frm.doc.docstatus !== 1 || !has_unacknowledged) return;

    frappe.db.get_value('Employee', frm.doc.requested_by, 'user_id')
        .then(r => {
            const requested_user = r.message.user_id;

            if (frappe.session.user !== requested_user) return;

            const btn = frm.add_custom_button(__('Acknowledge Receipt'), () => {
                frappe.confirm(
                    __('Are you sure you want to acknowledge receipt of these assets?'),
                    () => {
                        frappe.call({
                            method: "beams.beams.doctype.asset_request.asset_request.acknowledge_assets",
                            args: {
                                asset_request_name: frm.doc.name
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.msgprint(r.message);
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                );
            });

            btn.css({
                backgroundColor: '#079b8aff',
                color: 'white',
                border: 'none',
                fontWeight: '500'
            });
        });
}

