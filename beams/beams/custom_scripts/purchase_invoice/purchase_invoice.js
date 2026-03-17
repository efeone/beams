frappe.ui.form.on('Purchase Invoice', {
	setup: function(frm) {
		handle_workflow_button(frm);
	},
	invoice_type: function (frm) {
		if (frm.doc.invoice_type === 'Stringer Bill') {

			frm.fields_dict['items'].grid.get_field('item_code').get_query = function (doc, cdt, cdn) {
				return {
					filters: [
						["is_stock_item", "=", 0]
					]
				};
			};

			frm.set_query('supplier', function () {
				return {
					filters: { is_stringer: 1 }
				};
			});

		} else if (frm.doc.invoice_type === 'Normal') {

		} else if (frm.doc.invoice_type === 'General') {

			frm.fields_dict['items'].grid.get_field('item_code').get_query = function (doc, cdt, cdn) {
				return {};
			};

			frm.set_query('supplier', function () {
				return {};
			});
		}

		frm.clear_table('items');
		frm.refresh_field('items');
		frm.set_value('supplier', '');
	},
	supplier: function (frm) {
		fetch_supplier_details(frm, frm.doc.supplier);
	},
	onload: function (frm) {
		if (frm.doc.quotation) {
			frm.set_df_property('supplier', 'read_only', 1);
		}
	},
	refresh: function (frm) {
		fetch_advances_from_mcts(frm);
	},
	bureau: function (frm) {
		fetch_mode_of_payment_from_bureau(frm, frm.doc.bureau);
	}

});

frappe.ui.form.on('Stringer Work Details', {
	from_time: function (frm, cdt, cdn) {
		validate_time_and_calculate_hours(frm, cdt, cdn);
		validate_row_dates(frm, cdt, cdn);
	},

	to_time: function (frm, cdt, cdn) {
		validate_time_and_calculate_hours(frm, cdt, cdn);
		validate_row_dates(frm, cdt, cdn);
	},

	stringer_work_details_add: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		if (frm.doc.supplier_bureau) {
			frappe.model.set_value(cdt, cdn, 'bureau', frm.doc.supplier_bureau);
		}
	}
});

function validate_time_and_calculate_hours(frm, cdt, cdn) {
	var row = locals[cdt][cdn];

	if (row.from_time && row.to_time) {
		var from_time = new Date(row.from_time);
		var to_time = new Date(row.to_time);

		if (from_time >= to_time) {
			frappe.msgprint(__('From Date and Time cannot be after or equal to To Date and Time.'));
			frappe.model.set_value(cdt, cdn, 'to_time', null);
			frappe.model.set_value(cdt, cdn, 'hrs', 0);
		} else {
			var diff = (to_time - from_time) / (1000 * 60 * 60);
			frappe.model.set_value(cdt, cdn, 'hrs', diff.toFixed(2));
		}
	} else {
		frappe.model.set_value(cdt, cdn, 'hrs', 0);
	}
}
/**
  Ensures that all rows in the 'stringer_work_details' table have the same date.
*/
function validate_row_dates(frm, cdt, cdn) {
	var row = locals[cdt][cdn];

	if (row.from_time) {
		let first_row_date = null;
		let current_row_date = new Date(row.from_time).toDateString();

		frm.doc.stringer_work_details.forEach(existing_row => {
			if (existing_row.from_time && !first_row_date) {
				first_row_date = new Date(existing_row.from_time).toDateString();
			}
		});

		if (first_row_date && current_row_date !== first_row_date) {
			frappe.msgprint(__('All rows must have the same date'));
			frappe.model.set_value(cdt, cdn, 'from_time', null);
			frappe.model.set_value(cdt, cdn, 'to_time', null);
		}
	}
}

function handle_workflow_button(frm) {
	if (frm.doc.purchase_order_id) {
			$(document).ready(function () {
				var workflow_button = $(".btn.btn-primary.btn-sm[data-toggle='dropdown']");
				workflow_button.html('<span>S<span class="alt-underline">u</span>bmit</span>');
				workflow_button.find("svg").remove();
				workflow_button.on("click", function () {
					frm.savesubmit();
				});
				var workflow_button = $(".btn.btn-primary.btn-sm[data-toggle='dropdown']");
				workflow_button.html('<span>S<span class="alt-underline">u</span>bmit</span>');
				workflow_button.find("svg").remove();
				workflow_button.on("click", function () {
				frm.savesubmit();
				});
			});
	}
}
/**
  Fetches supplier details and updates the form fields.
  Sets the supplier's bureau and the bureau's mode of payment if available.
*/

function fetch_supplier_details(frm, supplier_name) {
	if (!supplier_name) return;

	frappe.db.get_value('Supplier', supplier_name, ['is_stringer', 'bureau'], function (r) {
		if (!r) return;

		frm.doc.supplier_bureau = r.bureau;
		frm.refresh_field('supplier_bureau');
		frm.set_value('bureau', r.bureau);

		fetch_mode_of_payment_from_bureau(frm, r.bureau);
	});
}

/**
  Fetches the Mode of Payment from the selected Bureau and updates the form.
*/
function fetch_mode_of_payment_from_bureau(frm, bureau) {
	if (!bureau) {
		frm.set_value('mode_of_payment', '');
		return;
	}

	frappe.db.get_value('Bureau', bureau, 'mode_of_payment', function (r) {
		if (r && r.mode_of_payment) {
			frm.set_value('mode_of_payment', r.mode_of_payment);
		} else {
			frm.set_value('mode_of_payment', '');
		}
	});
}

function fetch_advances_from_mcts(frm) {
    // When opened from Monthly Consolidated Trip Sheet, fetch advances for the supplier (like "Get Advances Paid")
		if (frappe.route_options && frappe.route_options.fetch_advances_from_mcts && frm.doc.supplier && frm.doc.__islocal) {
			delete frappe.route_options.fetch_advances_from_mcts;
			frappe.call({
				method: "run_doc_method",
				args: { docs: frm.doc, method: "set_advances" },
				callback: function (r) {
					if (!r.exc && r.docs && r.docs[0] && r.docs[0].advances && r.docs[0].advances.length) {
						frm.clear_table("advances");
						(r.docs[0].advances || []).forEach(function (row) {
							frm.add_child("advances", row);
						});
						frm.refresh_field("advances");
					}
				},
			});
		}
}