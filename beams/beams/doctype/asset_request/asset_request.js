// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Request', {
    onload_post_render: function(frm) {
        set_requested_by_if_empty(frm);
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
        return_allocated_assets(frm);
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
                    { label: 'Bundle', fieldname: 'bundle', fieldtype: 'Link', options: 'Asset Bundle', in_list_view: 1 },
                ]
            }
        ],
        size: 'large',
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

/**
 * Adds an "Acknowledge Receipt" button for the requester to confirm receipt of allocated assets.
 */

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

function set_requested_by_if_empty(frm) {
    if (!frm.doc.requested_by) {
        frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                if (r.message) frm.set_value('requested_by', r.message.name);
            });
    }
}

/**
 * Adds a custom button to return allocated assets if any are unreturned
 */
function return_allocated_assets(frm) {
    if (frm.doc.allocated_assets && !frm.doc.allocated_assets.some(row => !row.returned)) return;
    const btn = frm.add_custom_button(__('Return Allocated Assets'), () => {
        open_return_assets_popup(frm);
    });
    btn.css({
                backgroundColor: '#1878d2ff',
                color: 'white',
                border: 'none',
                fontWeight: '500'
            });
}


/**
 * Opens a dialog to process the return of selected allocated assets and create an Asset Movement
 */

function open_return_assets_popup(frm) {

    const asset_ids = (frm.doc.allocated_assets || [])
    .filter(row => !row.returned && row.asset)
    .map(row => row.asset);

    
    // Fetch asset details
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Asset",
            filters: [["name", "in", asset_ids]],
            fields: ["name", "location", "custodian", "company"]
        },
        callback: function (res) {
            const assets = res.message || [];

            const rows = assets.map(asset => ({
                asset: asset.name,
                source_location: asset.location || "",
                from_employee: asset.custodian || "",
                target_location: "",
                to_employee: "",
                company: asset.company || ""
            }));

            let d = new frappe.ui.Dialog({
                title: __('Return Allocated Assets'),
                fields: [
                    {
                        label: __("Purpose"),
                        fieldname: "purpose",
                        fieldtype: "Data",
                        default: "Receipt",
                        reqd: 1,
                        read_only: 1
                    },
                    { 
                        label: 'Target Location', 
                        fieldname: 'target_location', 
                        fieldtype: 'Link', 
                        options: 'Location', 
                        reqd: 1 
                    },
                    {
                        label: 'Items',
                        fieldname: 'items_table',
                        fieldtype: 'Table',
                        cannot_add_rows: 0,
                        in_place_edit: true,
                        data: rows,
                        fields: [
                            { label: 'Asset', fieldname: 'asset', fieldtype: 'Link', options: 'Asset', in_list_view: 1, reqd: 1 },
                            { label: 'Source Location', fieldname: 'source_location', fieldtype: 'Data', in_list_view: 1, read_only: 1 },
                        ]
                    }
                ],
                size: 'large',
                primary_action_label: __('Return'),
                primary_action: function (values) {
                    const items = values.items_table || [];


                    frappe.confirm(
                        __('Are you sure you want to return assets?'),
                        function () {
                            const movement_doc = {
                                doctype: "Asset Movement",
                                purpose: values.purpose,
                                transaction_date: frappe.datetime.now_datetime(),
                                company: frm.doc.company || (items[0].company || ""),
                                // to_employee: values.assigned_to,
                                reference_doctype: "Asset Request",
                                reference_name: frm.doc.name,
                                assets: items.map(row => ({
                                    asset: row.asset,
                                    source_location: row.source_location,
                                    target_location: values.target_location,
                                    from_employee: frm.doc.requested_by
                                }))
                            };

                            frappe.call({
                                method: "frappe.client.insert",
                                args: { doc: movement_doc },
                                callback: function (r) {
                                    if (r.message) {
                                        frappe.msgprint(__('Asset Movement created in Draft.'));

                                        frappe.call({
                                            method: "beams.beams.doctype.asset_request.asset_request.mark_assets_returned",
                                            args: {
                                                docname: frm.doc.name,
                                                assets: items.map(item => item.asset)
                                            },
                                            callback: function (res) {
                                                if (!res.exc) {
                                                    frappe.msgprint(__('Marked assets as returned.'));
                                                    frm.reload_doc();
                                                    d.hide();
                                                }
                                            }
                                        });

                                    }
                                }
                            });
                        }
                    );
                }
            });

            d.show();
        }
    });
}
