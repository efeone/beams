// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on("Fuel Card Log", {
  setup(frm) {
	frm.set_query("fuel_card", () => {
	  let used = [];
	  frappe.call({
		method: "frappe.client.get_list",
		async: false,
		args: {
		  doctype: "Fuel Card Log",
		  fields: ["fuel_card"],
		  filters: { docstatus: ["!=", 2] }
		},
		callback(r) {
		  used = r.message.map(d => d.fuel_card);
		}
	  });
	  return { filters: [["Fuel Card", "name", "not in", used]] };
	});
  },

  refresh(frm) {
	if (!frm.is_new()) {
	  frm.add_custom_button('Ownership Transaction', () => {
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
			reqd: 1,
			onchange: function() {
			  const selected_date = this.get_value();
			  const today_date = frappe.datetime.get_today();
			  if (selected_date > today_date) {
				if (!this._show_date_error) {
				  this._show_date_error = true;
				  frappe.msgprint({
					title: 'Invalid Date',
					indicator: 'red',
					message: 'Future dates are not allowed. Please select today or a past date.'
				  });
				  this.set_value(today_date);
				  setTimeout(() => {
					this._show_date_error = false;
				  }, 100);
				}
			  }
			}
		  }
		], (values) => {
		  let last_row = frm.doc.ownered_by && frm.doc.ownered_by.slice(-1)[0];

		  if (last_row && last_row.ownership === values.new_owner) {
			frappe.msgprint(`The last owner is already "${values.new_owner}". No new row added.`);
			frm.set_value('current_holder', values.new_owner);
			return;
		  }

		  let child = frm.add_child('ownered_by', {
			ownership: values.new_owner,
			date: values.date
		  });
		  frm.refresh_field('ownered_by');
		  frm.set_value('current_holder', values.new_owner);
		  frm.save();
		}, 'Add', 'Save');
	  }, 'Add');

	  // Button: Set Recharge History
	  frm.add_custom_button('Recharge', () => {
		frappe.prompt([
		  {
			label: 'Refilling Amount',
			fieldname: 'recharge_amount',
			fieldtype: 'Float',
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
		  },
		  {
			label: 'Vehicle',
			fieldname: 'vehicle',
			fieldtype: 'Link',
			options: 'Vehicle'
		  }
		], (values) => {
			if (values.recharge_amount > frm.doc.fuel_card_limit) {
				frappe.msgprint({
					title: __('Validation Error'),
					message: __('Refilling Amount {0} is more than Fuel Card Limit {1}',
						[values.recharge_amount, frm.doc.fuel_card_limit]),
					indicator: 'red'
				});
				return;
			}

		  let child = frm.add_child('recharge_history', {
			recharge_amount: values.recharge_amount,
			recharged_date: values.recharged_date,
			voucher_no: values.voucher_no,
			vehicle:values.vehicle
		  });
		  frm.refresh_field('recharge_history');
		  frm.save();
		}, 'Add', 'Save');
	  }, 'Add');
	}
  }
});
