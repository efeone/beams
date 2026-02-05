
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
		clear_checkbox_exceed(frm);
		calculate_total_amount(frm);

	},
	is_budgeted: function(frm){	
		clear_checkbox_exceed(frm);
	}
});

frappe.ui.form.on('Material Request Item', {
	amount: function(frm, cdt, cdn) {
		calculate_total_amount(frm);
	},
	qty: function(frm, cdt, cdn) {
		calculate_total_amount(frm);
	},
	rate: function(frm, cdt, cdn) {
		calculate_total_amount(frm);
	},
	items_remove: function(frm, cdt, cdn) {
		calculate_total_amount(frm);
	}
});

/**
 * Calculates total amount from qty × rate for all items
 */
function calculate_total_amount(frm) {
	let total = 0.0;
	if (frm.doc.items && frm.doc.items.length) {
		frm.doc.items.forEach(function(item) {
			total += (item.amount || 0);
		});
	}
	frm.set_value('total_amount', total);
}

/**
* Clears the "is_budget_exceeded" checkbox if "is_budgeted" is unchecked.
*/
function clear_checkbox_exceed(frm){
	if (frm.doc.is_budgeted == 0){
		frm.set_value("is_budget_exceeded", 0);
	}
}
