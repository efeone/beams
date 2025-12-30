// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Batta Claim', {
	validate: function(frm) {
		calculate_total_distance_travelled(frm);
		calculate_total_daily_batta(frm);
		update_all_daily_batta(frm);
		calculate_batta(frm);
		calculate_total_hours(frm);
	},
	batta: function(frm) {
		update_all_daily_batta(frm);
	},
	ot_batta: function(frm) {
		update_all_daily_batta(frm);
	},
	room_rent_batta: function(frm) {
		calculate_batta(frm);
		if (frm.doc.room_rent_batta < 0) {
			frappe.msgprint({
				message: "Room Rent Batta cannot be negative.",
				indicator: "red"
			});
			frm.set_value("room_rent_batta", 0);
		}
	},
	daily_batta_without_overnight_stay: function(frm) {
		calculate_batta(frm);
		if (frm.doc.daily_batta_without_overnight_stay < 0) {
			frappe.msgprint({
				message: "Daily Batta Without Overnight Stay cannot be negative.",
				indicator: "red"
			});
			frm.set_value("daily_batta_without_overnight_stay", 0);
		}
	},
	daily_batta_with_overnight_stay: function(frm) {
		calculate_batta(frm);
		if (frm.doc.daily_batta_with_overnight_stay < 0) {
			frappe.msgprint({
				message: "Daily Batta With Overnight Stay cannot be negative.",
				indicator: "red"
			});
			frm.set_value("daily_batta_with_overnight_stay", 0);
		}
	},
	is_travelling_outside_kerala: function(frm) {
		update_all_daily_batta(frm);
		calculate_allowance(frm);
	},
	is_overnight_stay: function(frm) {
		update_all_daily_batta(frm);
		calculate_allowance(frm);
		frm.doc.work_detail.forEach(row => {
		  set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
		  set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
		})
	},
	is_avail_room_rent: function(frm) {
		toggle_room_rent_batta_field(frm);
		update_all_daily_batta(frm);
		calculate_allowance(frm);
	},
	is_delhi_bureau: function(frm) {
	  frm.doc.work_detail.forEach(row => {
		set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
		set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
	  })
	},
	refresh: function(frm) {
		toggle_room_rent_batta_field(frm);
		clear_checkbox_exceed(frm);
		frappe.call({
			method: "beams.beams.doctype.batta_claim.batta_claim.get_batta_policy_values",
			callback: function(response) {
				if (response.message) {
					let is_actual_daily_batta_without_overnight_stay = response.message.is_actual__;
					let is_actual_daily_batta_with_overnight_stay = response.message.is_actual_;
					let is_actual_room_rent_batta = response.message.is_actual;
					let is_actual_food_allowance = response.message.is_actual___;

					frm.set_df_property('daily_batta_without_overnight_stay', 'read_only', is_actual_daily_batta_without_overnight_stay == 0);
					frm.set_df_property('daily_batta_with_overnight_stay', 'read_only', is_actual_daily_batta_with_overnight_stay == 0);
					frm.set_df_property('room_rent_batta', 'read_only', is_actual_room_rent_batta == 0);

					frm.refresh_field('daily_batta_without_overnight_stay');
					frm.refresh_field('daily_batta_with_overnight_stay');
					frm.refresh_field('room_rent_batta');

					frm.fields_dict['work_detail'].grid.update_docfield_property('breakfast', 'read_only', is_actual_food_allowance == 0);
					frm.fields_dict['work_detail'].grid.update_docfield_property('lunch', 'read_only', is_actual_food_allowance == 0);
					frm.fields_dict['work_detail'].grid.update_docfield_property('dinner', 'read_only', is_actual_food_allowance == 0);

					frm.refresh_field('work_detail');
				}
			}
		});
	},
	is_budgeted: function(frm){
		clear_checkbox_exceed(frm);
	}
});

frappe.ui.form.on('Work Detail', {
	distance_travelled_km: function(frm, cdt, cdn) {
		calculate_total_distance_travelled(frm);
		setTimeout(() => {
			set_batta_for_food_allowance(frm, cdt, cdn);
			calculate_batta(frm, cdt, cdn);
		}, 30);
	},
	daily_batta: function(frm, cdt, cdn) {
		calculate_total_batta(frm, cdt, cdn);
	},
	breakfast: function(frm, cdt, cdn) {
		let child = locals[cdt][cdn];
		if (child.breakfast < 0) {
			frappe.msgprint({
				message: "Breakfast cannot be negative.",
				indicator: "red"
			});

			frappe.model.set_value(cdt, cdn, "breakfast", 0);
		}
		calculate_total_food_allowance(frm, cdt, cdn);
		calculate_total_batta(frm, cdt, cdn);
	},
	lunch: function(frm, cdt, cdn) {
		let child = locals[cdt][cdn];
		if (child.lunch < 0) {
			frappe.msgprint({
				message: "Lunch cannot be negative.",
				indicator: "red"
			});

			frappe.model.set_value(cdt, cdn, "lunch", 0);
		}
		calculate_total_food_allowance(frm, cdt, cdn);
		calculate_total_batta(frm, cdt, cdn);
	},
	dinner: function(frm, cdt, cdn) {
		let child = locals[cdt][cdn];
		if (child.dinner < 0) {
			frappe.msgprint({
				message: "Dinner cannot be negative.",
				indicator: "red"
			});

			frappe.model.set_value(cdt, cdn, "dinner", 0);
		}
		calculate_total_food_allowance(frm, cdt, cdn);
		calculate_total_batta(frm, cdt, cdn);
	},
	total_batta: function(frm, cdt, cdn) {
	  calculate_total_daily_batta(frm, cdt, cdn);
	},
	total_food_allowance: function(frm, cdt, cdn) {
		calculate_total_batta(frm, cdt, cdn);
	},
	work_detail_add: function(frm, cdt, cdn) {
	  const { origin, destination } = frm.doc;
		frappe.model.set_value(cdt, cdn, 'origin', origin);
		frappe.model.set_value(cdt, cdn, 'destination', destination);

		calculate_total_distance_travelled(frm);
		calculate_total_daily_batta(frm);
		calculate_total_hours(frm);
		setTimeout(() => {
			calculate_batta(frm, cdt, cdn);
		}, 30);
	},
	work_detail_remove: function(frm, cdt, cdn) {
		calculate_total_distance_travelled(frm);
		calculate_total_daily_batta(frm);
		calculate_total_hours(frm);
		setTimeout(() => {
			calculate_batta(frm, cdt, cdn);
		}, 30);
	},
	total_hours: function(frm, cdt, cdn) {
		calculate_daily_batta(frm, cdt, cdn);
		calculate_total_hours(frm,cdt,cdn);
		set_batta_for_food_allowance(frm, cdt, cdn);
	},
	ot_hours: function(frm, cdt, cdn) {
		calculate_daily_batta(frm, cdt, cdn);
	},
	from_date_and_time: function(frm, cdt, cdn) {
		calculate_hours(frm, cdt, cdn);
		calculate_daily_batta(frm, cdt, cdn);
		setTimeout(() => {
			set_batta_for_food_allowance(frm, cdt, cdn);
			calculate_batta(frm, cdt, cdn);
		}, 500);
	},
	to_date_and_time: function(frm, cdt, cdn) {
	  let row = locals[cdt][cdn];

	  if (row.from_date_and_time && row.to_date_and_time) {
		  let from_date = new Date(row.from_date_and_time);
		  let to_date = new Date(row.to_date_and_time);

		  if (to_date <= from_date) {
			  frappe.msgprint(__('To Date & Time must be greater than From Date & Time'));
			  frappe.model.set_value(cdt, cdn, 'to_date_and_time', null);
			  return;
		}
		calculate_hours(frm, cdt, cdn);
		calculate_daily_batta(frm, cdt, cdn);
		setTimeout(() => {
			set_batta_for_food_allowance(frm, cdt, cdn);
			calculate_batta(frm, cdt, cdn);
		}, 500);
	}
  }
});

/*
  Toggle room_rent_batta field visibility based on is_avail_room_rent checkbox
*/
function toggle_room_rent_batta_field(frm) {
	if (frm.doc.is_avail_room_rent) {
		frm.set_df_property('room_rent_batta', 'hidden', 0);
	} else {
		frm.set_df_property('room_rent_batta', 'hidden', 1);
		frm.set_value('room_rent_batta', 0);
	}
	frm.refresh_field('room_rent_batta');
}

/*
  Calculates the total distance traveled based on all work detail entries.
*/
function calculate_total_distance_travelled(frm) {
	let totalDistance = 0;
	frm.doc.work_detail.forEach(row => {
		totalDistance += row.distance_travelled_km || 0;
	});
	frm.set_value('total_distance_travelled_km', totalDistance);
}

/*
  Calculates the total hours worked based on all work detail entries.
*/
function calculate_total_hours(frm) {
	let totalHours = 0;
	frm.doc.work_detail.forEach(row => {
		totalHours += row.total_hours || 0;
	});
	frm.set_value('total_hours', totalHours);
}

/*
  Calculates hours worked for a specific row based on the from and to date/time fields.
*/
function calculate_hours(frm, cdt, cdn) {
	let row = frappe.get_doc(cdt, cdn);
	if (row.from_date_and_time && row.to_date_and_time) {
		let total_hours = (new Date(row.to_date_and_time) - new Date(row.from_date_and_time)) / (1000 * 60 * 60);
				frappe.model.set_value(cdt, cdn, 'total_hours', total_hours.toFixed(2));
	}
}

/*
  Calculates the daily batta based on the total hours worked and the batta type.
*/
function calculate_daily_batta(frm, cdt, cdn) {
	let row = frappe.get_doc(cdt, cdn);
	let total_hours = row.total_hours || 0;
	let distance = row.distance_travelled_km || 0;
	let number_of_days = Math.max(1, Math.ceil(total_hours / 24));
	frappe.model.set_value(cdt, cdn, "number_of_days", number_of_days);
	frappe.model.set_value(cdt, cdn, "daily_batta", 0);
	if (frm.doc.batta_based_on === 'Daily') {
	if (distance >= 100 && total_hours >= 8) {
		let parent_batta = frm.doc.daily_batta_without_overnight_stay || 0;
		let daily_batta = number_of_days * parent_batta;

		frappe.model.set_value(cdt, cdn, "daily_batta", daily_batta);

	}
	}
}

/*
  Updates daily batta for all child rows in the work detail table.
*/
function update_all_daily_batta(frm) {
	if (frm.doc.work_detail) {
		frm.doc.work_detail.forEach(row => {
			calculate_daily_batta(frm, row.doctype, row.name);
		});
	}
}

/*
  Calculates the total daily batta across all work detail entries.
*/
function calculate_total_daily_batta(frm) {
	let totalDailyBatta = 0;
	frm.doc.work_detail.forEach(row => {
		totalDailyBatta += row.total_batta || 0;
	});
	frm.set_value('total_daily_batta', totalDailyBatta);
}

/* Sets the batta-based options based on the selected batta type.*/
function set_batta_based_on_options(frm) {
	if (frm.doc.batta_type === 'Internal') {
		frm.set_df_property('batta_based_on', 'options', ['Daily']);
		frm.set_value('batta_based_on', 'Daily');
	}
}

/* Calculates total batta based on room rent, daily batta with and without overnight stay.*/
function calculate_batta(frm) {
	let total_batta = (frm.doc.room_rent_batta || 0)
					+ (frm.doc.daily_batta_without_overnight_stay || 0)
					+ (frm.doc.daily_batta_with_overnight_stay || 0);

	frm.set_value('batta', total_batta);
}

function calculate_allowance(frm) {
	if (!frm.doc.designation.length) {
		frappe.msgprint(__("Please select a designation."));
		return;
	}

	frappe.call({
		method: "beams.beams.doctype.batta_claim.batta_claim.calculate_batta_allowance",
		args: {
			designation: frm.doc.designation,
			is_travelling_outside_kerala: frm.doc.is_travelling_outside_kerala || 0,
			is_overnight_stay: frm.doc.is_overnight_stay || 0,
			is_avail_room_rent: frm.doc.is_avail_room_rent || 0,
			total_distance_travelled_km: frm.doc.total_distance_travelled_km || 0,
			total_hours: frm.doc.total_hours || 0
		},
		callback: function(r) {
			if (r.message) {
				frm.set_value("room_rent_batta", r.message.room_rent_batta);
				frm.set_value("daily_batta_with_overnight_stay", r.message.daily_batta_with_overnight_stay);
				frm.set_value("daily_batta_without_overnight_stay", r.message.daily_batta_without_overnight_stay);
				frm.set_value("batta", r.message.batta);
			}
		}
	});
}
/* Determines eligibility for food allowance and updates fields accordingly.*/
function set_batta_for_food_allowance(frm, cdt, cdn) {
	let child = locals[cdt][cdn];
	let designation = frm.doc.designation;
	let is_overnight_stay = frm.doc.is_overnight_stay;
	let is_delhi_bureau = frm.doc.is_delhi_bureau;

	if (!designation) return;
	let distance = parseFloat(child.distance_travelled_km) || 0;
	let total_hours = parseFloat(child.total_hours) || 0;

	let is_eligible = false;
	if (is_delhi_bureau) {
		if (distance >= 30 && total_hours >= 4) {
			is_eligible = true;
		} else {
			frappe.model.set_value(child.doctype, child.name, "breakfast", 0);
			frappe.model.set_value(child.doctype, child.name, "lunch", 0);
			frappe.model.set_value(child.doctype, child.name, "dinner", 0);
			frappe.model.set_value(child.doctype, child.name, "total_food_allowance", 0);
			return;
		}
	} 
	else {
		if (distance >= 50 && total_hours >= 6 && total_hours <= 8) {
			is_eligible = true;
		}
		else if (distance >= 100 && total_hours >= 8) {
			frappe.model.set_value(child.doctype, child.name, "breakfast", 0);
			frappe.model.set_value(child.doctype, child.name, "lunch", 0);
			frappe.model.set_value(child.doctype, child.name, "dinner", 0);
			frappe.model.set_value(child.doctype, child.name, "total_food_allowance", 0);
			return;
		}
	}
	if (is_overnight_stay) {
		frappe.model.set_value(child.doctype, child.name, "breakfast", 0);
		frappe.model.set_value(child.doctype, child.name, "lunch", 0);
		frappe.model.set_value(child.doctype, child.name, "dinner", 0);
		frappe.model.set_value(child.doctype, child.name, "total_food_allowance", 0);
		return;
	}
	if (is_eligible && !is_overnight_stay) {
		frappe.call({
			method: "beams.beams.doctype.batta_claim.batta_claim.get_batta_for_food_allowance",
			args: {
				designation: designation,
				from_date_time: child.from_date_and_time,
				to_date_time: child.to_date_and_time,
				total_hrs: total_hours,
				is_delhi_bureau: is_delhi_bureau
			},
			callback: function (r) {
				if (r && r.message) {
					let response = r.message;
					frappe.model.set_value(child.doctype, child.name, "breakfast", response.break_fast);
					frappe.model.set_value(child.doctype, child.name, "lunch", response.lunch);
					frappe.model.set_value(child.doctype, child.name, "dinner", response.dinner);
					frappe.model.set_value(child.doctype, child.name, "total_food_allowance", response.break_fast + response.lunch + response.dinner);
				}
			}
		});
	}
}

/* Calculation of Total Food Allowance. */
function calculate_total_food_allowance(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	frm.call({
		method: "beams.beams.doctype.batta_claim.batta_claim.calculate_total_food_allowance",
		args: {
			breakfast: row.breakfast || 0,
			lunch: row.lunch || 0,
			dinner: row.dinner || 0
		},
		callback: function(r) {
			if (r.message) {
				row.total_food_allowance = r.message.total_food_allowance;
				frm.refresh_field("work_detail");
			}
		}
	});
}

/* Calculation of total batta based on daily batta and food allowance. */
function calculate_total_batta(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	frm.call({
		method: "beams.beams.doctype.batta_claim.batta_claim.calculate_total_batta",
		args: {
			daily_batta: row.daily_batta || 0,
			total_food_allowance: row.total_food_allowance || 0
		},
		callback: function(r) {
			if (r.message) {
				frappe.model.set_value(cdt, cdn, "total_batta", r.message.total_batta);
				frm.refresh_field("work_detail");
			}
		}
	});
}

/**
* Clears the "is_budget_exceed" checkbox if "is_budgeted" is unchecked.
*/    
function clear_checkbox_exceed(frm){
	if(frm.doc.is_budgeted == 0){
		frm.set_value("is_budget_exceed", 0);
	}
}
