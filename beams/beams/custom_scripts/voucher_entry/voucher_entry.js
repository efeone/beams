frappe.ui.form.on('Voucher Entry', {
	bureau: function(frm) {
	  // Triggered when the 'bureau' field is updated
		if (frm.doc.bureau) {
			frappe.db.get_value('Bureau', frm.doc.bureau, ['cost_center', 'company'], function(r) {
				if (r) {
					frm.set_value('cost_center', r.cost_center);
					frm.set_value('company', r.company);
				}
			});
		}
	}
});

frappe.ui.form.on("Voucher Entry", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Petty Cash Request'), function () {
				show_petty_cash_dialog(frm);
			});
		}
		update_parent_checkboxes(frm);
		update_budget_exceeded_visibility(frm);
	},
	voucher_accounts_add: function(frm) {
		update_parent_checkboxes(frm);
	},
	voucher_accounts_remove: function(frm) {
		update_parent_checkboxes(frm);
	}
});

frappe.ui.form.on('Voucher Account', {
	is_budgeted: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		if (!row.is_budgeted) {
			frappe.model.set_value(cdt, cdn, "is_budget_exceeded", 0);
		}

		update_parent_checkboxes(frm);
		update_budget_exceeded_visibility(frm);
	},
	is_budget_exceeded: function(frm) {
		update_parent_checkboxes(frm);
	}
});

/*
 * Updates the parent document's `is_budgeted` and `is_budget_exceeded` fields
 * based on the values in the child table `voucher_accounts`.
*/
function update_parent_checkboxes(frm) {
	let is_budgeted_all = true;
	let is_budget_exceeded_any = false;

	if (frm.doc.voucher_accounts && frm.doc.voucher_accounts.length > 0) {
		frm.doc.voucher_accounts.forEach(function(row) {
			if (row.is_budgeted !== 1 && row.is_budgeted !== '1') {
				is_budgeted_all = false;
			}
			if (row.is_budget_exceeded === 1 || row.is_budget_exceeded === '1') {
				is_budget_exceeded_any = true;
			}
		});
	} else {
		is_budgeted_all = true;
		is_budget_exceeded_any = false;
	}

	let parent_is_budgeted = frm.doc.is_budgeted ? cint(frm.doc.is_budgeted) : 0;
	let parent_is_budget_exceeded = frm.doc.is_budget_exceeded ? cint(frm.doc.is_budget_exceeded) : 0;

	let new_is_budgeted = is_budgeted_all ? 1 : 0;
	let new_is_budget_exceeded = is_budget_exceeded_any ? 1 : 0;

	if (parent_is_budgeted !== new_is_budgeted) {
		frm.set_value("is_budgeted", new_is_budgeted);
	}

	if (parent_is_budget_exceeded !== new_is_budget_exceeded) {
		frm.set_value("is_budget_exceeded", new_is_budget_exceeded);
	}

	frm.refresh_field('is_budgeted');
	frm.refresh_field('is_budget_exceeded');
}

function show_petty_cash_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Petty Cash Request"),
		fields: [
			{
				fieldname: "bureau",
				label: __("Bureau"),
				fieldtype: "Link",
				options: "Bureau",
				reqd: 1,
				default: frm.doc.bureau
			},
			{
				fieldname: "mode_of_payment",
				label: __("Mode of Payment"),
				fieldtype: "Link",
				options: "Mode of Payment",
				reqd: 1,
				default: frm.doc.mode_of_payment
			},
			{
				fieldname: "account",
				label: __("Account"),
				fieldtype: "Link",
				options: "Account",
				reqd: 1,
				default: frm.doc.account
			},
			{
				fieldname: "requested_amount",
				label: __("Requested Amount"),
				fieldtype: "Currency",
				reqd: 1
			}
		],
		primary_action_label: __("Submit"),
		primary_action(values) {
			submit_petty_cash_request(frm, values, d);
		}
	});

	d.show();
}

function submit_petty_cash_request(frm, values, dialog) {
	frappe.call({
		method: "beams.beams.custom_scripts.voucher_entry.voucher_entry.create_petty_cash_request",
		args: {
			voucher_entry_name: frm.doc.name,
			bureau: values.bureau,
			mode_of_payment: values.mode_of_payment,
			account: values.account,
			requested_amount: values.requested_amount
		},
		callback: function (response) {
			if (response.message.status === "success") {
				frappe.msgprint(__("Petty Cash Request Created Successfully!"));
				dialog.hide();
			} else {
				frappe.msgprint(__("Error: " + response.message));
			}
		}
	});
}

/*
 Handles showing / hiding is_budget_exceeded
*/
function update_budget_exceeded_visibility(frm) {
	frm.toggle_display("is_budget_exceeded", frm.doc.is_budgeted == 1);

	if (!frm.doc.is_budgeted) {
		frm.set_value("is_budget_exceeded", 0);
	}
}
