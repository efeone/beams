// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bureau Trip Sheet", {
	refresh: function (frm) {
		filter_supplier_field(frm);
		// Only recalculate allowance for new docs; saved docs already have values from server (avoids "Not Saved" after save)
		if (frm.is_new()) {
			calculate_allowance(frm);
		} else {
			set_batta_policy_properties(frm);
		}
		filter_employee_field(frm);
		show_batta_button(frm);
		add_settlement_journal_entry_button(frm);
	},
	validate: function (frm) {
		calculate_batta(frm);
		calculate_total_distance_travelled(frm);
		calculate_hours(frm);
		calculate_total_daily_batta(frm);
		calculate_total_ot_batta(frm);
	},
	batta: function (frm) {
	},
	ot_batta: function (frm) {
		calculate_ot_batta(frm);
	},
	daily_batta_with_overnight_stay: function (frm) {
		calculate_batta(frm);
	},
	daily_batta_without_overnight_stay: function (frm) {
		calculate_batta(frm);
	},
	total_daily_batta: function (frm) {
		calculate_total_driver_batta(frm);
	},
	total_ot_batta: function (frm) {
		calculate_total_driver_batta(frm);
	},
	is_overnight_stay: function (frm) {
		calculate_allowance(frm);
	},
	is_travelling_outside_kerala: function (frm) {
		calculate_allowance(frm);
	},
	total_distance_travelled_km: function (frm) {
		calculate_allowance(frm);
	},
	total_hours: function(frm) {
		calculate_allowance(frm);
	},
	initial_odometer_reading: function(frm) {
		calculate_distance_from_odometer_parent(frm);
	},
	final_odometer_reading: function(frm) {
		calculate_distance_from_odometer_parent(frm);
	},
	starting_date_and_time: function(frm) {
		// Update total hours and OT batta when trip start time changes
		calculate_hours_and_days(frm);
		calculate_allowance(frm);
	},
	ending_date_and_time: function(frm) {
		// Update total hours and OT batta when trip end time changes
		calculate_hours_and_days(frm);
		calculate_allowance(frm);
	},
	supplier: function(frm) {
		if (frm.doc.supplier) {
			frappe.db.get_value("Supplier", frm.doc.supplier, "average_mileage_kmpl", function(r) {
				if (r && r.average_mileage_kmpl) {
					frm.set_value("average_mileage_kmpl", r.average_mileage_kmpl);
				}
			});
		}
		set_batta_policy_properties(frm);
	},
	distance_travelledkm: function(frm) {
		calculate_fuel(frm);
	},
	fuel_rate__litre: function(frm) {
		calculate_fuel(frm);
	},
	average_mileage_kmpl: function(frm) {
		calculate_fuel(frm);
	},
	onload: function(frm) {
		filter_supplier_field(frm);
	}
});

/* Set filter for supplier field */
function filter_supplier_field(frm) {
	frm.set_query("supplier", function () {
		return {
			filters: {
				is_transporter: 1
			}
		};
	});
}

/* Function to filter active employees */
function filter_employee_field(frm) {
	frm.set_query("employees", () => {
		return {
			filters: {
				status: "Active",
				bureau: frm.doc.bureau
			}
		};
	});
}

/* Function to set Batta Policy properties */
function set_batta_policy_properties(frm) {
	const batta_fields = [
		"daily_batta_with_overnight_stay",
		"daily_batta_without_overnight_stay",
		"total_food_allowance",
		"breakfast",
		"lunch",
		"dinner"
	];

	function make_all_readonly() {
		batta_fields.forEach(field => frm.set_df_property(field, "read_only", 1));
		frm.refresh_fields(batta_fields);
	}

	if (!frm.doc.supplier) {
		make_all_readonly();
		return;
	}

	frappe.call({
		method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_batta_policy_values",
		args: {
			supplier: frm.doc.supplier
		},
		callback: function (response) {
			if (!response.message || Object.keys(response.message).length === 0) {
				make_all_readonly();
				return;
			}

			let policy   = response.message;
			let distance = flt(frm.doc.total_distance_travelled_km || 0);
			let hours    = flt(frm.doc.total_hours || 0);
			let is_overnight = frm.doc.is_overnight_stay ? 1 : 0;

			let flag_with    = policy.is_actual_with    === 1;
			let flag_without = policy.is_actual_without === 1;
			let flag_food    = policy.is_actual_food    === 1;

			let allow_with    = false;
			let allow_without = false;
			let allow_food    = false;

			if (is_overnight) {
				allow_with = flag_with;

			} else if (distance >= 100 && hours >= 8) {
				allow_without = flag_without;

			} else if (distance >= 50 && hours >= 6) {
				allow_food = flag_food;
			}

			frm.set_df_property("daily_batta_with_overnight_stay",    "read_only", allow_with    ? 0 : 1);
			frm.set_df_property("daily_batta_without_overnight_stay", "read_only", allow_without ? 0 : 1);
			frm.set_df_property("total_food_allowance",               "read_only", allow_food    ? 0 : 1);
			frm.set_df_property("breakfast",                          "read_only", allow_food    ? 0 : 1);
			frm.set_df_property("lunch",                              "read_only", allow_food    ? 0 : 1);
			frm.set_df_property("dinner",                             "read_only", allow_food    ? 0 : 1);

			frm.refresh_fields(batta_fields);
		}
	});
}

// Calculate total hours on the parent and then compute OT batta using the parent's OT batta rate.
function calculate_hours_and_days(frm) {
	// Ensure total hours on the parent are up to date.
	calculate_hours(frm);
	// Then calculate OT batta based on those hours.
	calculate_ot_batta(frm);
}

// Calculate OT batta on the parent document based on total hours and supplier-specific OT working hours.
function calculate_ot_batta(frm) {
	const total_hours = frm.doc.total_hours || 0;
	// Require supplier and some hours before hitting the server
	if (!frm.doc.supplier || !total_hours) {
		return;
	}

	frappe.call({
		method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_ot_working_hours",
		args: { supplier: frm.doc.supplier },
		callback: function (r) {
			if (r && r.message != null) {
				const ot_working_hours = parseFloat(r.message) || 0;
				const ot_hours = total_hours > ot_working_hours ? (total_hours - ot_working_hours) : 0;
				const ot_rate = frm.doc.ot_batta || 0; // per-hour OT batta fetched from Supplier
				const total_ot_batta = ot_hours * ot_rate;

				frm.set_value('total_ot_batta', total_ot_batta);
				calculate_total_driver_batta(frm);
			}
		}
	});
}

function update_all_ot_batta(frm) {
}

/* Trip batta = daily rate × number of days (or food allowance total) — matches server validate */
function calculate_batta(frm) {
	let trip_batta_amount = 0;
	if (frm.doc.total_food_allowance) {
		trip_batta_amount = flt(frm.doc.total_food_allowance);
	} else {
		const total_trip_hours = flt(frm.doc.total_hours);
		const number_of_days = Math.max(1, Math.ceil(total_trip_hours / 24));
		if (frm.doc.is_overnight_stay) {
			trip_batta_amount = number_of_days * flt(frm.doc.daily_batta_with_overnight_stay);
		} else {
			trip_batta_amount = number_of_days * flt(frm.doc.daily_batta_without_overnight_stay);
		}
	}
	frm.set_value("batta", trip_batta_amount);
	calculate_total_daily_batta(frm);
	calculate_total_driver_batta(frm);
}

// Calculate total batta for the entire trip by summing up daily batta and OT batta for all rows in the child table, and update the total batta field in the parent form.
function calculate_total_batta_for_row(frm, cdt, cdn) {
	calculate_total_daily_batta(frm);
	calculate_total_driver_batta(frm);
}

// Calculate total distance travelled by summing up distance travelled for all rows in the child table, and update the total distance travelled field in the parent form.
function calculate_total_distance_travelled(frm) {
	frm.set_value('total_distance_travelled_km', frm.doc.distance_travelledkm || 0);
	frm.refresh_field("total_distance_travelled_km");
}

// Calculate total hours for the entire trip by summing up total hours for all rows in the child table, and update the total hours field in the parent form.
function calculate_hours(frm) {
	if (frm.doc.check_in_time && frm.doc.ending_date_and_time) {
		let start = new Date(frm.doc.check_in_time);
		let end = new Date(frm.doc.ending_date_and_time);
		let total_hours = end > start ? Math.round((end - start) / (1000 * 60 * 60) * 100) / 100 : 0;
		frm.set_value('total_hours', total_hours);
	} else {
		frm.set_value('total_hours', 0);
	}
	frm.refresh_field("total_hours");
}

// Calculate total daily batta by summing up daily batta for all rows in the child table, and update the total daily batta field in the parent form.
function calculate_total_daily_batta(frm) {
	frm.set_value('total_daily_batta', frm.doc.batta || 0);
	frm.refresh_field("total_daily_batta");
}

//  Calculate total OT batta on the parent (wrapper to keep existing hooks working).
function calculate_total_ot_batta(frm) {
	calculate_ot_batta(frm);
}

/* Calculate total driver batta as the sum of total daily batta and total OT batta */
function calculate_total_driver_batta(frm) {
	let total_daily_batta = frm.doc.total_daily_batta || 0;
	let total_ot_batta = frm.doc.total_ot_batta || 0;

	frm.set_value('total_driver_batta', total_daily_batta + total_ot_batta);
	frm.refresh_field("total_driver_batta");
}

/* Calculate fuel consumption and total fuel expense from distance, mileage and rate */
function calculate_fuel(frm) {
	let distance = parseFloat(frm.doc.distance_travelledkm) || 0;
	let mileage = parseFloat(frm.doc.average_mileage_kmpl) || 0;
	let rate = parseFloat(frm.doc.fuel_rate__litre) || 0;

	if (distance && mileage) {
		let fuel_consumption = distance / mileage;
		frm.set_value("fuel_consumption_l", fuel_consumption);
		frm.refresh_field("fuel_consumption_l");
	}
}

/* Determines eligibility for batta/food allowance per row and updates fields accordingly. */
function calculate_row_allowances(frm, cdt, cdn) {
	let child = locals[cdt][cdn];
	let designation = frm.doc.designation || "Driver";
	let is_overnight_stay = frm.doc.is_overnight_stay || 0;
	let is_travelling_outside_kerala = frm.doc.is_travelling_outside_kerala || 0;
	let distance = child.distance_travelled_km || 0;
	let total_hrs = child.total_hours || 0;
	let num_days = Math.max(1, Math.ceil(total_hrs / 24));

	// Reset
	frappe.model.set_value(child.doctype, child.name, "daily_batta", 0);
	frappe.model.set_value(child.doctype, child.name, "breakfast", 0);
	frappe.model.set_value(child.doctype, child.name, "lunch", 0);
	frappe.model.set_value(child.doctype, child.name, "dinner", 0);
	frappe.model.set_value(child.doctype, child.name, "total_food_allowance", 0);


	if (is_overnight_stay) {
		frappe.call({
			method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.calculate_batta_allowance",
			args: {
				designation: designation,
				is_travelling_outside_kerala: is_travelling_outside_kerala,
				is_overnight_stay: 1,
				total_distance_travelled_km: distance,
				total_hours: total_hrs
			},
			callback: function (r) {
				if (r.message) {
					let rate = r.message.daily_batta_with_overnight_stay || 0;
					let daily = num_days * rate;
					frappe.model.set_value(child.doctype, child.name, "daily_batta", daily);
					frm.set_value("daily_batta_with_overnight_stay", rate);
					calculate_total_batta_for_row(frm, child.doctype, child.name);
				}
			}
		});
		return;
	}

	if (distance >= 100 && total_hrs >= 8) {
		frappe.call({
			method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.calculate_batta_allowance",
			args: {
				designation: designation,
				is_travelling_outside_kerala: is_travelling_outside_kerala,
				is_overnight_stay: 0,
				total_distance_travelled_km: distance,
				total_hours: total_hrs
			},
			callback: function (r) {
				if (r.message) {
					let rate = r.message.daily_batta_without_overnight_stay || 0;
					let daily = num_days * rate;
					frappe.model.set_value(child.doctype, child.name, "daily_batta", daily);
					frm.set_value("daily_batta_without_overnight_stay", rate);
					calculate_total_batta_for_row(frm, child.doctype, child.name);
				}
			}
		});
		return;
	} else if ((distance >= 50 && distance < 100 && total_hrs >= 6) || (distance >= 100 && total_hrs >= 6 && total_hrs < 8)) {
		frappe.call({
			method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_batta_for_food_allowance",
			args: {
				designation: designation,
				from_date_time: child.from_date_and_time,
				to_date_time: child.to_date_and_time,
				total_hrs: total_hrs
			},
			callback: function (r) {
				if (r && r.message) {
					let response = r.message;
					frappe.model.set_value(child.doctype, child.name, "breakfast", response.break_fast);
					frappe.model.set_value(child.doctype, child.name, "lunch", response.lunch);
					frappe.model.set_value(child.doctype, child.name, "dinner", response.dinner);
					let food_total = response.break_fast + response.lunch + response.dinner;
					frappe.model.set_value(child.doctype, child.name, "total_food_allowance", food_total);
					calculate_total_batta_for_row(frm, child.doctype, child.name);
				}
			}
		});
		return;
	}
}

// Calculate allowance for the entire trip based on designation, whether travelling outside Kerala, whether there is an overnight stay, total distance travelled and total hours, and update the respective fields in the parent form.
function calculate_allowance(frm) {
	frappe.call({
		method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.calculate_batta_allowance",
		args: {
			designation: frm.doc.designation || "Driver",
			is_travelling_outside_kerala: frm.doc.is_travelling_outside_kerala || 0,
			is_overnight_stay: frm.doc.is_overnight_stay || 0,
			total_distance_travelled_km: frm.doc.total_distance_travelled_km || 0,
			total_hours: frm.doc.total_hours || 0
		},
		callback: function(r) {
			if (r.message) {
				frm.set_value("daily_batta_with_overnight_stay", r.message.daily_batta_with_overnight_stay);
				frm.set_value("daily_batta_without_overnight_stay", r.message.daily_batta_without_overnight_stay);
				// Keep client behavior aligned with backend: trip batta uses daily rate x number_of_days.
				calculate_batta(frm);
				set_batta_policy_properties(frm);

			}
		}
	});
}


// Calculate distance travelled based on initial and final odometer readings, and update the distance travelled field in the child table. Also perform validation to ensure that readings are non-negative and final reading is greater than initial reading.
function calculate_distance_from_odometer_parent(frm) {
	let initial = frm.doc.initial_odometer_reading;
	let final = frm.doc.final_odometer_reading;
	if (initial != null && initial !== undefined && (parseInt(initial) || 0) < 0) {
		frappe.msgprint({ title: __('Invalid Odometer Reading'), message: __('Initial Odometer Reading cannot be negative.'), indicator: 'red' });
		frm.set_value('initial_odometer_reading', null);
		frm.set_value('distance_travelledkm', 0);
		return;
	}
	if (final != null && final !== undefined && (parseInt(final) || 0) < 0) {
		frappe.msgprint({ title: __('Invalid Odometer Reading'), message: __('Final Odometer Reading cannot be negative.'), indicator: 'red' });
		frm.set_value('final_odometer_reading', null);
		frm.set_value('distance_travelledkm', 0);
		return;
	}
	if (initial != null && initial !== undefined && final != null && final !== undefined) {
		initial = parseInt(initial) || 0;
		final = parseInt(final) || 0;
		if (final <= initial) {
			frappe.msgprint({ title: __('Invalid Odometer Reading'), message: __('Final must be greater than Initial.'), indicator: 'red' });
			frm.set_value('final_odometer_reading', null);
			frm.set_value('distance_travelledkm', 0);
			return;
		}
		frm.set_value('distance_travelledkm', final - initial);
		calculate_total_distance_travelled(frm);
		calculate_allowance(frm);
		calculate_fuel(frm);
	}
}


// Calculate distance travelled based on initial and final odometer readings, and update the distance travelled field in the child table. Also perform validation to ensure that readings are non-negative and final reading is greater than initial reading.
function calculate_distance_from_odometer(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (!row) return;

	let initial = row.initial_odometer_reading;
	let final = row.final_odometer_reading;

	// Validate Initial Odometer Reading
	if (initial !== null && initial !== undefined) {
		initial = parseInt(initial) || 0;

		// Initial Odometer Reading should not be negative
		if (initial < 0) {
			frappe.msgprint({
				title: __('Invalid Odometer Reading'),
				message: __('Row {0}: Initial Odometer Reading cannot be negative (got {1})', [row.idx, initial]),
				indicator: 'red'
			});
			frappe.model.set_value(cdt, cdn, 'initial_odometer_reading', null);
			frappe.model.set_value(cdt, cdn, 'distance_travelled_km', 0);
			return;
		}
	}

	// Validate Final Odometer Reading
	if (final !== null && final !== undefined) {
		final = parseInt(final) || 0;

		// Final Odometer Reading should not be negative
		if (final < 0) {
			frappe.msgprint({
				title: __('Invalid Odometer Reading'),
				message: __('Row {0}: Final Odometer Reading cannot be negative (got {1})', [row.idx, final]),
				indicator: 'red'
			});
			frappe.model.set_value(cdt, cdn, 'final_odometer_reading', null);
			frappe.model.set_value(cdt, cdn, 'distance_travelled_km', 0);
			return;
		}
	}

	// Calculate distance only if both readings are present
	if (row.initial_odometer_reading && row.final_odometer_reading) {
		initial = parseInt(row.initial_odometer_reading);
		final = parseInt(row.final_odometer_reading);
		// Final Odometer Reading must be greater than Initial Odometer Reading
		if (final <= initial) {
			frappe.msgprint({
				title: __('Invalid Odometer Reading'),
				message: __('Row {0}: Final Odometer Reading must be greater than Initial Odometer Reading', [row.idx]),
				indicator: 'red'
			});
			frappe.model.set_value(cdt, cdn, 'final_odometer_reading', null);
			frappe.model.set_value(cdt, cdn, 'distance_travelled_km', 0);
			return;
		}

		// Calculate distance travelled
		let distance = final - initial;
		frappe.model.set_value(cdt, cdn, 'distance_travelled_km', distance);

		setTimeout(() => {
			calculate_total_distance_travelled(frm);
			calculate_row_allowances(frm, cdt, cdn);
		}, 100);
	}
}

// Show "Request Batta" button if the user is eligible to request batta claim based on the trip sheet details and user's permissions.
function show_batta_button(frm) {
	if (!frm.is_new()) {
			frappe.call({
				method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.can_show_request_batta_button",
				args: { bureau_trip_sheet: frm.doc.name },
				callback: function (r) {
					if (r.message) {
						create_batta_claim(frm);
					}
				}
			});
		}
}


// create batta claim from trip sheet
function create_batta_claim(frm) {
	frm.add_custom_button(__("Request Batta"), function () {
		frappe.call({
			method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.create_batta_claim",
			args: { bureau_trip_sheet: frm.doc.name },
			callback: function (response) {
				if (response.message) {
					let doc = frappe.model.sync(response.message)[0];
					frappe.set_route("Form", doc.doctype, doc.name);
				}
			}
		});
	});
}


// Patty Cash Payment: we have given (paid) the supplier the amount.
// JE: Debit Supplier payable, Credit Bank/Cash. Supplier account from Supplier doctype Default Accounts table.
function add_settlement_journal_entry_button(frm) {
	if (!frm.is_new()) {
		frm.add_custom_button(__("Patty Cash Payment"), function () {
			open_settlement_dialog(frm);
		});
	}
}

function open_settlement_dialog(frm) {
	if (!frm.doc.bureau) {
		frappe.msgprint(__("Please select a Bureau first."), __("Cannot create settlement"));
		return;
	}

	const default_amount = frm.doc.total_driver_batta || 0;

	// Get Bureau's mode of payment so popup uses only that
	frappe.db.get_value("Bureau", frm.doc.bureau, "mode_of_payment", function (r) {
		const bureau_mop = r && r.mode_of_payment;

		const d = new frappe.ui.Dialog({
			title: __("Create Settlement Journal Entry"),
			fields: [
				{
					fieldname: "mode_of_payment",
					fieldtype: "Link",
					label: __("Mode of Payment"),
					options: "Mode of Payment",
					reqd: 1,
					default: bureau_mop || "",
					get_query: function () {
						// Restrict to this Bureau's mode of payment
						if (bureau_mop) {
							return { filters: { name: bureau_mop } };
						}
						return {};
					},
				},
				{
					fieldname: "amount",
					fieldtype: "Currency",
					label: __("Amount"),
					reqd: 1,
					default: default_amount,
				},
				{
					fieldname: "supplier_account_info",
					fieldtype: "Small Text",
					label: __("Supplier account (from Supplier)"),
					read_only: 1,
				},
			],
			size: "medium",
			primary_action_label: __("Create"),
			primary_action: function () {
				const values = d.get_values();
				if (!values) return;
				d.hide();
				submit_settlement_journal_entry(frm, values.mode_of_payment, values.amount);
			},
		});

		// Show which supplier account will be used (fetched from Supplier doctype)
		frappe.call({
			method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_supplier_payable_account",
			args: {
				supplier: frm.doc.supplier,
				company: frm.doc.company,
			},
			callback: function (r) {
				if (r.message && d.fields_dict.supplier_account_info) {
					d.fields_dict.supplier_account_info.set_value(r.message);
					d.fields_dict.supplier_account_info.df.hidden = 0;
					d.fields_dict.supplier_account_info.refresh();
				}
			},
		});

		d.show();
	});
}

function submit_settlement_journal_entry(frm, mode_of_payment, amount) {
	frappe.call({
		method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.create_settlement_journal_entry",
		args: {
			bureau_trip_sheet: frm.doc.name,
			mode_of_payment: mode_of_payment,
			amount: amount,
		},
		callback: function (response) {
			if (response.message) {
				frappe.msgprint({
					title: __("Success"),
					message: __("Settlement Journal Entry {0} created in Draft.", [response.message]),
					indicator: "green"
				});
			}
		}
	});
}