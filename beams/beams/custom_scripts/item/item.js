frappe.ui.form.on('Item', {
	item_group: function(frm) {
		if (frm.doc.item_group === 'Services') {
			frm.set_value('is_stock_item', 0);
			clear_warehouse_fields(frm);
		}
	},
	
	refresh: function(frm) {
		if (frm.doc.item_group === 'Services' && frm.doc.is_stock_item === 1) {
			frm.set_value('is_stock_item', 0);
			clear_warehouse_fields(frm);
		}
	},    
	
	is_stock_item: function(frm) {
		if (frm.doc.is_stock_item === 0) {
			clear_warehouse_fields(frm);
		}
	}
});

frappe.ui.form.on('Item Default', {
	item_defaults_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (frm.doc.item_group === 'Services' || !frm.doc.is_stock_item) {
			frappe.model.set_value(cdt, cdn, 'default_warehouse', '');
		}
	}
});

/**
 * Clears all warehouse assignments from Item Defaults child table.
 * 
 * This function iterates through all rows in the item_defaults child table
 * and sets the default_warehouse field to empty string, then refreshes the
 * field to update the UI.
 */
function clear_warehouse_fields(frm) {    
	if (frm.doc.item_defaults) {
		frm.doc.item_defaults.forEach(row => {
			frappe.model.set_value(row.doctype, row.name, 'default_warehouse', '');
		});
	}
	frm.refresh_field('item_defaults');
}