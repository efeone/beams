// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Template', {
	refresh: function (frm) {
		set_filters(frm);
	},
	department: function (frm) {
		set_filters(frm);
		frm.set_value('division', null);
		if (!frm.doc.department) {
			frm.set_value('division',)
			clear_budget_items(frm);
		}
		set_filters(frm);
	},
	company: function (frm) {
		frm.set_value('department', null);
		frm.set_value('division', null);
		if (frm.doc.company) {
			clear_budget_items(frm);
		}
	}
});

frappe.ui.form.on('Budget Template Item', {
	cost_head: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.cost_head || !frm.doc.company) {
			frappe.model.set_value(cdt, cdn, 'cost_category',);
			frappe.model.set_value(cdt, cdn, 'budget_group',);
			frappe.model.set_value(cdt, cdn, 'account_head',);
			return;
		}
		else {
			let cost_head = row.cost_head;
			// Fetching default account for cost head
			frappe.call("beams.beams.utils.get_default_account_of_cost_head", {
				cost_head: cost_head,
				company: frm.doc.company
			}).then(r => {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, 'account_head', r.message);
				}
				else {
					frappe.model.set_value(cdt, cdn, 'cost_head',);
					frappe.model.set_value(cdt, cdn, 'cost_category',);
					frappe.model.set_value(cdt, cdn, 'budget_group',);
					frappe.throw({
						title: __('Missing Default Account'),
						message: __(
							'No default account found for Cost Head : <b>{0}</b> for the selected company.', [cost_head]
						)
					});
				}
			})
		}
	},
});

// Set query filters for link fields
function set_filters(frm) {
	frm.set_query('department', function () {
		return {
			filters: {
				company: frm.doc.company,
				is_group: 0,
			}
		};
	});
	frm.set_query('division', function () {
		return {
			filters: {
				department: frm.doc.department,
				company: frm.doc.company
			}
		};
	});
	frm.set_query('region', function () {
		return {
			filters: {
				company: frm.doc.company
			}
		};
	});
	frm.set_query("cost_center", function () {
		return {
			filters: {
				company: frm.doc.company,
				is_group: 0,
				disabled: 0
			}
		}
	});
	frm.set_query('budget_head', function () {
		return {
			query: 'beams.beams.doctype.budget_template.budget_template.get_budget_approver_employees',
			filters: {
				company: frm.doc.company || "",
				department: frm.doc.department || ""
			}
		};
	});
}

// Clear budget items table
function clear_budget_items(frm) {
	frm.clear_table('budget_template_items');
	frm.refresh_field('budget_template_items');
}