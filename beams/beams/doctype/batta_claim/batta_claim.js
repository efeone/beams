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
    onload: function(frm) {
        handle_designation_based_on_batta_type(frm);
    },
    batta_type: function(frm) {
        handle_designation_based_on_batta_type(frm);
        set_batta_based_on_options(frm);
    },
    employee: function(frm) {
        handle_designation_based_on_batta_type(frm);
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
    total_distance_travelled_km: function(frm) {
        calculate_allowance(frm);
    },
    total_hours: function(frm) {
        calculate_allowance(frm);
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
        update_all_daily_batta(frm);
        calculate_allowance(frm);
    },
    is_delhi_bureau: function(frm) {
      frm.doc.work_detail.forEach(row => {
        set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
        set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
      })
    },
    //fetching policy values and setting fields read-only accordingly
    refresh: function(frm) {
        frappe.call({
            method: "beams.beams.doctype.batta_claim.batta_claim.get_batta_policy_values",
            callback: function(response) {
                if (response.message) {
                    let is_actual_daily_batta_without_overnight_stay = response.message.is_actual__;
                    let is_actual_daily_batta_with_overnight_stay = response.message.is_actual_;
                    let is_actual_room_rent_batta = response.message.is_actual;
                    let is_actual_food_allowance = response.message.is_actual___;

                    // Set read-only based on conditions
                    frm.set_df_property('daily_batta_without_overnight_stay', 'read_only', is_actual_daily_batta_without_overnight_stay == 0);
                    frm.set_df_property('daily_batta_with_overnight_stay', 'read_only', is_actual_daily_batta_with_overnight_stay == 0);
                    frm.set_df_property('room_rent_batta', 'read_only', is_actual_room_rent_batta == 0);

                    // Refresh the fields to reflect the changes
                    frm.refresh_field('daily_batta_without_overnight_stay');
                    frm.refresh_field('daily_batta_with_overnight_stay');
                    frm.refresh_field('room_rent_batta');

                    frm.fields_dict['work_detail'].grid.update_docfield_property('breakfast', 'read_only', is_actual_food_allowance == 0);
                    frm.fields_dict['work_detail'].grid.update_docfield_property('lunch', 'read_only', is_actual_food_allowance == 0);
                    frm.fields_dict['work_detail'].grid.update_docfield_property('dinner', 'read_only', is_actual_food_allowance == 0);

                    // Refresh child table
                    frm.refresh_field('work_detail');
                }
            }
        });
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

            frappe.model.set_value(cdt, cdn, "breakfast", 0); // Reset to 0
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

            frappe.model.set_value(cdt, cdn, "lunch", 0); // Reset to 0
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

            frappe.model.set_value(cdt, cdn, "dinner", 0); // Reset to 0
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
        }, 30);
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
        }, 30);
    }
  }
});

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

    if (!row.total_hours) row.total_hours = 0;

    let number_of_days = Math.max(1, Math.ceil(row.total_hours / 24)); // Ensure at least 1 day
    let daily_batta = 0;

    if (frm.doc.batta_based_on === 'Daily') {
        daily_batta = number_of_days * (frm.doc.batta || 0);
    }

    frappe.model.set_value(cdt, cdn, 'number_of_days', number_of_days);
    frappe.model.set_value(cdt, cdn, 'daily_batta', daily_batta);
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

/* Function to handle designation field based on batta_type */
function handle_designation_based_on_batta_type(frm) {
    if (frm.doc.batta_type === 'Internal' && frm.doc.employee) {
        // Fetch and set designation when batta_type is Internal
        designation = frappe.db.get_value('Employee', frm.doc.employee, 'designation', function (r) {
            if (r && r.designation) {
                frm.set_value('designation', r.designation);
            } else {
                frappe.msgprint(__('Designation not found for the selected employee.'));
            }
        });
    } else if (frm.doc.batta_type === 'External') {
        frm.set_value('designation', '');
    }
}

/* Sets the batta-based options based on the selected batta type.*/
function set_batta_based_on_options(frm) {
    if (frm.doc.batta_type === 'External') {
        frm.set_df_property('batta_based_on', 'options', 'Hours');
        frm.set_value('batta_based_on', 'Hours');
    } else {
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

    if (designation.length <= 0) {
        return;
    }
    let is_eligible = false;

    if (is_delhi_bureau) {
        if (child.distance_travelled_km >= 30 && child.total_hours > 4) {
            is_eligible = true;
        }
    } else {
        if (child.distance_travelled_km >= 50 && child.distance_travelled_km < 100 && child.total_hours > 6) {
            is_eligible = true;
        }
    }

    if (is_overnight_stay) {
        frappe.model.set_value(child.doctype, child.name, "breakfast", 0);
        frappe.model.set_value(child.doctype, child.name, "lunch", 0);
        frappe.model.set_value(child.doctype, child.name, "dinner", 0);
        frappe.model.set_value(child.doctype, child.name, "total_food_allowance", 0);
        return;
    }
    else if (is_eligible && !is_overnight_stay) {
        frappe.call({
            method: "beams.beams.doctype.batta_claim.batta_claim.get_batta_for_food_allowance",
            args: {
                designation: designation,
                from_date_time: child.from_date_and_time,
                to_date_time: child.to_date_and_time,
                total_hrs: child.total_hours,
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
    row.total_food_allowance = (row.breakfast || 0) + (row.lunch || 0) + (row.dinner || 0);

    frm.refresh_field("work_detail");
}

/* Calculation of total batta based on daily batta and food allowance. */
function calculate_total_batta(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "total_batta", (row.daily_batta || 0) + (row.total_food_allowance || 0));
    frm.refresh_field("work_detail");
}
