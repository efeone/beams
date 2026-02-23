// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cost Head", {
	refresh(frm) {
		set_filters(frm);
	},
});

function set_filters(frm) {
	frm.set_query('default_account', 'accounts', (frm, cdt, cdn) => {
		const row = locals[cdt][cdn];
		return {
			filters: {
				is_group: 0,
				disabled: 0,
				report_type: 'Profit and Loss',
				root_type: 'Expense',
				company: row.company
			}
		}
	})
}