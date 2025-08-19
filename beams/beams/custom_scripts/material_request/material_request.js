
frappe.ui.form.on('Material Request', {
    onload(frm) {
        if (!frm.doc.requested_by) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    if (r.message) {
                        frm.set_value('requested_by', r.message.name);
                    }
                });
        }
    },
	refresh(frm) {
		// Show buttons only if workflow_state is Approved by HOD or Approved by Admin
		if (["Approved by HOD", "Approved by Admin"].includes(frm.doc.workflow_state)) {
			add_asset_movement_button(frm);
			add_stock_entry_button(frm);
		}
	}
});

/**
 * Add "Asset Movement" button to Material Request
 * → Allows user to create an Asset Movement for fixed asset items
 */
function add_asset_movement_button(frm) {
	frm.add_custom_button(__("Asset Movement"), () => {
		const item_codes = (frm.doc.items || []).map(row => row.item_code);

		if (!item_codes.length) {
			frappe.msgprint({
				title: __("Missing Items"),
				message: __("No items in this Material Request."),
				indicator: "red"
			});
			return;
		}

		frappe.db.get_list("Item", {
			filters: { name: ["in", item_codes], is_fixed_asset: 1 },
			fields: ["name"]
		}).then(items => {
			if (!items?.length) {
				frappe.msgprint({
					title: __("No Fixed Assets"),
					message: __("No Fixed Asset items found in this Material Request."),
					indicator: "orange"
				});
				return;
			}

			const fixed_asset_items = frm.doc.items.filter(row =>
				items.some(i => i.name === row.item_code)
			);

			const default_items = fixed_asset_items.flatMap(row =>
				Array.from({ length: row.qty }, () => ({
					item: row.item_code,
					qty: 1,
					asset: ""
				}))
			);

			const fields = [
				{
					label: __("Assigned To"),
					fieldname: "assigned_to",
					fieldtype: "Link",
					options: "User",
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
					fieldname: "asset_movement_details",
					label: __("Asset Movement Details"),
					fieldtype: "Table",
					reqd: 1,
					data: default_items,
					fields: [
						{
							label: __("Item"),
							fieldname: "item",
							fieldtype: "Link",
							options: "Item",
							in_list_view: 1,
							reqd: 1
						},
						{
							label: __("Quantity"),
							fieldname: "qty",
							fieldtype: "Int",
							in_list_view: 1,
							reqd: 1
						},
						{
							label: __("Asset"),
							fieldname: "asset",
							fieldtype: "Link",
							options: "Asset",
							reqd: 1,
							in_list_view: 1,
							get_query: () => ({
								filters: { location: frm.doc.location }
							})
						}
					]
				}
			];

			const dialog = new frappe.ui.Dialog({
				title: __("Asset Movement"),
				fields,
				primary_action_label: __("Submit"),
				primary_action(values) {
					frappe.call({
						method: "beams.beams.custom_scripts.material_request.material_request.map_asset_movement_from_mr",
						args: {
							source_name: frm.doc.name,
							assigned_to: values.assigned_to,
							items: values.asset_movement_details,
							purpose: values.purpose
						},
						callback(r) {
							if (!r.exc) {
								frappe.show_alert({
									message: __('Asset Movement {0} created and submitted', [r.message]),
									indicator: 'green'
								});
								frappe.set_route("Form", "Asset Movement", r.message);
							}
						}
					});
				}
			});

			// Auto-set Assigned To
			const fallback_user = frappe.session.user;
			if (frm.doc.requested_by) {
				frappe.db.get_value("Employee", frm.doc.requested_by, "user_id").then(r => {
					dialog.set_value("assigned_to", r.message?.user_id || fallback_user);
				});
			} else {
				dialog.set_value("assigned_to", fallback_user);
			}

			dialog.show();
		});
	}, __("Create"));
}

/**
 * Add "Create Stock Entry" button to Material Request
 * → Allows user to create a Stock Entry for non-fixed-asset stock items
 */
function add_stock_entry_button(frm) {
	frm.add_custom_button(__('Create Stock Entry'), () => {
		if (!frm.doc.items?.length) {
			frappe.msgprint({
				title: __("Missing Items"),
				message: __("No items in this Material Request."),
				indicator: "red"
			});
			return;
		}

		let item_codes = frm.doc.items.map(d => d.item_code);

		frappe.db.get_list('Item', {
			filters: {
				name: ['in', item_codes],
				is_fixed_asset: 0,
				is_stock_item: 1
			},
			fields: ['name', 'stock_uom']
		}).then(items_data => {
			if (!items_data?.length) {
				frappe.msgprint({
					title: __("No Stock Items"),
					message: __("No stock-managed items to create Stock Entry."),
					indicator: "orange"
				});
				return;
			}

			let stock_items = frm.doc.items
				.filter(row => items_data.some(i => i.name === row.item_code))
				.map(row => {
					let item = items_data.find(i => i.name === row.item_code);
					return {
						item_code: row.item_code,
						qty: row.qty,
						uom: item.stock_uom
					};
				});

			frappe.db.get_single_value('BEAMS Admin Settings', 'default_source_warehouse')
				.then(default_warehouse => {
					let d = new frappe.ui.Dialog({
						title: __('Create Stock Entry'),
						fields: [
							{
								fieldtype: 'Link',
								fieldname: 'source_warehouse',
								options: 'Warehouse',
								label: __('Source Warehouse'),
								default: default_warehouse,
								reqd: 1
							},
							{
								fieldtype: 'Table',
								fieldname: 'items',
								label: __('Items'),
								in_place_edit: true,
								data: stock_items,
								fields: [
									{fieldtype: 'Data', fieldname: 'item_code', label: __('Item'), read_only: 1, in_list_view: 1},
									{fieldtype: 'Float', fieldname: 'qty', label: __('Qty'), in_list_view: 1},
									{fieldtype: 'Data', fieldname: 'uom', label: __('UOM'), read_only: 1, in_list_view: 1}
								]
							}
						],
						primary_action_label: __('Create Stock Entry'),
						primary_action(values) {
							frappe.call({
								method: "beams.beams.custom_scripts.material_request.material_request.create_stock_entry_from_mr",
								args: {
									material_request: frm.doc.name,
									source_warehouse: values.source_warehouse,
									items: values.items
								},
								callback(r) {
									if (r.message) {
										frappe.show_alert({
											message: __('Stock Entry Created: {0}', [r.message]),
											indicator: 'green'
										});
										d.hide();
									}
								}
							});
						}
					});
					d.show();
				});
		});
	}, __("Create"));
}


