// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bureau Trip Sheet", {
	refresh: function (frm) {
		filter_supplier_field(frm);
		// Only recalculate allowance for new docs; saved docs already have values from server (avoids "Not Saved" after save)
		if (frm.is_new()) {
			calculate_allowance(frm);
		}
		set_batta_policy_properties(frm);
		filter_employee_field(frm);
		show_batta_button(frm);
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
		calculate_hours(frm);
		calculate_allowance(frm);
	},
	ending_date_and_time: function(frm) {
		calculate_hours(frm);
		calculate_allowance(frm);
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
				status: "Active"
			}
		};
	});
}

/* Function to set Batta Policy properties */
function set_batta_policy_properties(frm) {
	frappe.call({
		method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_batta_policy_values",
		callback: function(response) {
			if (response.message) {
				let is_actual_daily_batta_without_overnight_stay = response.message.is_actual__;
				let is_actual_daily_batta_with_overnight_stay = response.message.is_actual_;

				frm.set_df_property('daily_batta_without_overnight_stay', 'read_only', is_actual_daily_batta_without_overnight_stay == 0);
				frm.set_df_property('daily_batta_with_overnight_stay', 'read_only', is_actual_daily_batta_with_overnight_stay == 0);

				frm.refresh_field('daily_batta_without_overnight_stay');
				frm.refresh_field('daily_batta_with_overnight_stay');
			}
		}
	});
}

// Calculate total hours, OT hours and number of days for a given row based on from and to date/time, and update the respective fields in the child table.
function calculate_hours_and_days(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (!row || !row.from_date_and_time || !row.to_date_and_time) return;
	let from_date = new Date(row.from_date_and_time);
	let to_date = new Date(row.to_date_and_time);
	let total_hours = (to_date - from_date) / (1000 * 60 * 60);
	total_hours = Math.round(total_hours * 100) / 100;
	if (!frm.doc.supplier) {
		frappe.msgprint(__('Please select a Supplier to calculate OT hours.'));
		return;
	}
	frappe.call({
		method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_ot_working_hours",
		args: { supplier: frm.doc.supplier },
		callback: function (r) {
			if (r.message != null) {
				let ot_working_hours = parseFloat(r.message) || 0;
				let ot_hours = total_hours > ot_working_hours ? total_hours - ot_working_hours : 0;
				frappe.model.set_value(cdt, cdn, 'total_hours', total_hours.toFixed(2));
				frappe.model.set_value(cdt, cdn, 'ot_hours', ot_hours.toFixed(2));
				frappe.model.set_value(cdt, cdn, 'number_of_days', Math.ceil(total_hours / 24));
				setTimeout(() => {
					calculate_ot_batta(frm, cdt, cdn);
					calculate_row_allowances(frm, cdt, cdn);
				}, 200);
			}
		}
	});
}

// Calculate OT batta for a given row based on OT hours and OT batta rate, and update the respective field in the child table.
function calculate_ot_batta(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (!row) return;
	let ot_hours = row.ot_hours || 0;
	let ot_batta = ot_hours * (frm.doc.ot_batta || 0);
	frappe.model.set_value(cdt, cdn, 'ot_batta', ot_batta);
}

function update_all_ot_batta(frm) {
}

/* Calculate total batta by summing daily batta values */
function calculate_batta(frm) {
	let batta = 0;

	if (frm.doc.is_overnight_stay) {
		batta = frm.doc.daily_batta_with_overnight_stay || 0;
	} else {
		batta = frm.doc.daily_batta_without_overnight_stay || 0;
	}

	frm.set_value("batta", batta);
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
	if (frm.doc.starting_date_and_time && frm.doc.ending_date_and_time) {
		let start = new Date(frm.doc.starting_date_and_time);
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

//  Calculate total OT batta by summing up OT batta for all rows in the child table, and update the total OT batta field in the parent form.
function calculate_total_ot_batta(frm) {
	frm.set_value('total_ot_batta', frm.doc.ot_batta || 0);
	frm.refresh_field("total_ot_batta");
}

/* Calculate total driver batta as the sum of total daily batta and total OT batta */
function calculate_total_driver_batta(frm) {
	let total_daily_batta = frm.doc.total_daily_batta || 0;
	let total_ot_batta = frm.doc.total_ot_batta || 0;

	frm.set_value('total_driver_batta', total_daily_batta + total_ot_batta);
	frm.refresh_field("total_driver_batta");
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
				frm.set_value("batta", (r.message.daily_batta_with_overnight_stay || 0) + (r.message.daily_batta_without_overnight_stay || 0));
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