
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
		frm.total_edited = false;
	},
	refresh(frm) {
		clear_checkbox_exceed(frm);
		if (!frm.total_edited) {
			calculate_total_amount(frm);
		}
	},
	total_amount: function(frm) {
		frm.total_edited = true;
	},
	is_budgeted: function(frm){	
		clear_checkbox_exceed(frm);
	}
});

frappe.ui.form.on('Material Request Item', {
	items_add: function(frm, cdt, cdn) {
		frm.total_edited = false;
		calculate_total_amount(frm);
	},
	amount: function(frm, cdt, cdn) {
		frm.total_edited = false;
		calculate_total_amount(frm);
	},
	qty: function(frm, cdt, cdn) {
		frm.total_edited = false;
		calculate_total_amount(frm);
	},
	rate: function(frm, cdt, cdn) {
		frm.total_edited = false;
		calculate_total_amount(frm);
	},
	items_remove: function(frm, cdt, cdn) {
		frm.total_edited = false;
		calculate_total_amount(frm);
	},
	item_code: function(frm, cdt, cdn) {
		frm.total_edited = false;
		calculate_total_amount(frm);
	}
});
/**
 * Calculates total amount from qty × rate for all items
 */
function calculate_total_amount(frm) {
	let total = 0.0;

	if (frm.doc.items?.length) {
		frm.doc.items.forEach(item => {
			total += flt(item.amount);
		});
	}

	if (!frm.total_edited) {
		frm.set_value('total_amount', total);
		frm.refresh_field('total_amount');
	}
}

/**
* Clears the "budget_exceeded" checkbox if "is_budgeted" is unchecked.
*/
function clear_checkbox_exceed(frm){
	if (frm.doc.is_budgeted == 0){
		frm.set_value("budget_exceeded", 0);
	}
}
