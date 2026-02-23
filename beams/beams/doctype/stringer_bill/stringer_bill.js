frappe.ui.form.on('Stringer Bill', {
	refresh: function (frm) {
		set_filters(frm);
	},
	is_budgeted: function (frm) {
		clear_checkbox_exceed(frm);
	}
});

frappe.ui.form.on('Stringer Bill Detail', {
	stringer_amount: function (frm) {
		calculate_total(frm);
	},
	stringer_bill_detail_remove: function (frm) {
		calculate_total(frm);
	},
	stringer_bill_detail_add: function (frm) {
		calculate_total(frm);
	}
});

function calculate_total(frm) {
	let total = 0;
	(frm.doc.stringer_bill_detail || []).forEach(row => {
		total += row.stringer_amount || 0;  // Summing up child table amounts
	});
	frm.set_value('stringer_amount', total);
}

/**
* Clears the "is_budget_exceeded" checkbox if "is_budgeted" is unchecked.
*/
function clear_checkbox_exceed(frm) {
	if (frm.doc.is_budgeted == 0) {
		frm.set_value("is_budget_exceeded", 0);
	}
}

function set_filters(frm) {
	frm.set_query('supplier', function () {
		return {
			filters: {
				'is_stringer': 1
			}
		};
	});
}