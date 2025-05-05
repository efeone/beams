// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on("Fuel Card Log", {
	refresh(frm) {
		if (!frm.is_new()) {
      
			// Button: Set Current Ownership
			frm.add_custom_button('Set Current Ownership', () => {
				frappe.prompt([
					{
						label: 'New Owner',
						fieldname: 'new_owner',
						fieldtype: 'Link',
						options: 'Employee',
						reqd: 1
					},
					{
						label: 'Date',
						fieldname: 'date',
						fieldtype: 'Date',
						default: frappe.datetime.get_today(),
						reqd: 1
					}
				], (values) => {
					let last_row = frm.doc.owered_by && frm.doc.owered_by.slice(-1)[0];

					if (last_row && last_row.ownership === values.new_owner) {
						frappe.msgprint(`The last owner is already "${values.new_owner}". No new row added.`);
						frm.set_value('current_holder', values.new_owner);
						return;
					}

					let child = frm.add_child('owered_by', {
						ownership: values.new_owner,
						date: values.date
					});
					frm.refresh_field('owered_by');
					frm.set_value('current_holder', values.new_owner);

					frappe.msgprint('Ownership updated successfully.');
				}, 'Set Current Ownership', 'Save');
			});

			// Button: Set Recharge History
			frm.add_custom_button('Set Recharge History', () => {
				frappe.prompt([
					{
						label: 'Recharge Amount',
						fieldname: 'recharge_amount',
						fieldtype: 'Int',
						reqd: 1
					},
					{
						label: 'Recharged Date',
						fieldname: 'recharged_date',
						fieldtype: 'Date',
						default: frappe.datetime.get_today(),
						reqd: 1
					},
					{
						label: 'Voucher No.',
						fieldname: 'voucher_no',
						fieldtype: 'Data',
						reqd: 1
					}
				], (values) => {
					let child = frm.add_child('recharge_history', {
						recharge_amount: values.recharge_amount,
						recharged_date: values.recharged_date,
						voucher_no: values.voucher_no
					});
					frm.refresh_field('recharge_history');
					frappe.msgprint('Recharge History updated successfully.');
				}, 'Set Recharge History', 'Save');
			});
		}
	}
});
