// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Details', {
    from_date_and_time: function (frm, cdt, cdn) {
        calculate_hours_and_days(frm, cdt, cdn);
        setTimeout(() => {
            set_batta_for_food_allowance(frm, cdt, cdn);
            calculate_batta(frm, cdt, cdn);
        }, 30);
    },
    to_date_and_time: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.from_date_and_time && row.to_date_and_time) {
            let from_date = new Date(row.from_date_and_time);
            let to_date = new Date(row.to_date_and_time);

            if (to_date <= from_date) {
                frappe.msgprint(__('To Date & Time must be greater than From Date & Time'));
                frappe.model.set_value(cdt, cdn, 'to_date_and_time', null);
                return;
            }
            setTimeout(() => {
                set_batta_for_food_allowance(frm, cdt, cdn);
                calculate_batta(frm, cdt, cdn);
        }, 30);
        }

        calculate_hours_and_days(frm, cdt, cdn);
    },
    total_hours: function (frm, cdt, cdn) {
        calculate_daily_batta(frm, cdt, cdn);
        calculate_ot_batta(frm, cdt, cdn);
        set_batta_for_food_allowance(frm, cdt, cdn);
    },
    ot_hours: function (frm, cdt, cdn) {
        calculate_ot_batta(frm, cdt, cdn);
    },
    breakfast: function (frm, cdt, cdn) {
       calculate_total_food_allowance(frm, cdt, cdn);
    },
    lunch: function (frm, cdt, cdn) {
       calculate_total_food_allowance(frm, cdt, cdn);
    },
    dinner: function (frm, cdt, cdn) {
       calculate_total_food_allowance(frm, cdt, cdn);
    },
    distance_travelled_km: function(frm, cdt, cdn) {
        calculate_total_distance_travelled(frm, cdt, cdn);
        setTimeout(() => {
            set_batta_for_food_allowance(frm, cdt, cdn);
            calculate_batta(frm, cdt, cdn);
        }, 30);
    },
    work_details_add:  function(frm, cdt, cdn) {

        calculate_total_distance_travelled(frm, cdt, cdn);

        calculate_hours(frm, cdt, cdn);

        calculate_total_daily_batta(frm, cdt, cdn);

        calculate_total_ot_batta(frm, cdt, cdn);

        setTimeout(() => {
            set_batta_for_food_allowance(frm, cdt, cdn);
            calculate_batta(frm, cdt, cdn);
        }, 30);
    },
    work_details_remove: function(frm, cdt, cdn) {
        calculate_total_distance_travelled(frm, cdt, cdn);
        calculate_hours(frm, cdt, cdn);
        calculate_total_daily_batta(frm, cdt, cdn);
        calculate_total_ot_batta(frm, cdt, cdn);
        setTimeout(() => {
            set_batta_for_food_allowance(frm, cdt, cdn);
            calculate_batta(frm, cdt, cdn);
        }, 30);
    },
    total_hours: function(frm, cdt, cdn) {
        calculate_hours(frm, cdt, cdn);
        set_batta_for_food_allowance(frm, cdt, cdn);
    },
    daily_batta: function(frm, cdt, cdn) {
        calculate_total_food_allowance(frm, cdt, cdn);
    },
    total_batta: function(frm, cdt, cdn) {
        calculate_total_daily_batta(frm, cdt, cdn);
    },
    ot_batta: function(frm, cdt, cdn) {
        calculate_total_ot_batta(frm, cdt, cdn);
    }

});

frappe.ui.form.on("Bureau Trip Sheet", {
    refresh: function (frm) {
        filter_supplier_field(frm);
        update_all_daily_batta(frm);
        update_all_ot_batta(frm);
        calculate_allowance(frm);
    },
    validate: function (frm) {
        update_all_daily_batta(frm);
        update_all_ot_batta(frm);
        calculate_batta(frm);
        calculate_total_distance_travelled(frm);
        calculate_hours(frm);
        calculate_total_daily_batta(frm);
        calculate_total_ot_batta(frm);
    },
    batta: function (frm) {
        update_all_daily_batta(frm);
    },
    ot_batta: function (frm) {
        update_all_ot_batta(frm);
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
        calculate_daily_batta(frm);
    },
    is_travelling_outside_kerala: function (frm) {
        calculate_allowance(frm);
        calculate_daily_batta(frm);
    },
    total_distance_travelled_km: function (frm) {
        calculate_allowance(frm);
    },
    total_hours: function(frm) {
        calculate_allowance(frm);
    },
    is_overnight_stay: function(frm) {
        calculate_allowance(frm);
        frm.doc.work_details.forEach(row => {
          set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
          set_batta_for_food_allowance(frm, row["doctype"], row["name"]);
        })

    },
    refresh: function(frm) {
        // Fetch Batta Policy values and set read-only properties
        frappe.call({
            method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_batta_policy_values",
            callback: function(response) {
                if (response.message) {
                    let is_actual_daily_batta_without_overnight_stay = response.message.is_actual__;
                    let is_actual_daily_batta_with_overnight_stay = response.message.is_actual_;
                    let is_actual_food_allowance = response.message.is_actual___;

                    // Set read-only properties
                    frm.set_df_property('daily_batta_without_overnight_stay', 'read_only', is_actual_daily_batta_without_overnight_stay == 0);
                    frm.set_df_property('daily_batta_with_overnight_stay', 'read_only', is_actual_daily_batta_with_overnight_stay == 0);

                    // Refresh fields
                    frm.refresh_field('daily_batta_without_overnight_stay');
                    frm.refresh_field('daily_batta_with_overnight_stay');

                    frm.fields_dict['work_details'].grid.update_docfield_property('breakfast', 'read_only', is_actual_food_allowance == 0);
                    frm.fields_dict['work_details'].grid.update_docfield_property('lunch', 'read_only', is_actual_food_allowance == 0);
                    frm.fields_dict['work_details'].grid.update_docfield_property('dinner', 'read_only', is_actual_food_allowance == 0);

                    // Refresh child table
                    frm.refresh_field('work_details');
                }
            }
        });

        // Call the supplier filter function
        filter_supplier_field(frm);
    },

    onload: function(frm) {
        // Ensure the filter is applied on form load as well
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

/* Calculate total hours, number of days, and overtime hours */
function calculate_hours_and_days(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.from_date_and_time && row.to_date_and_time) {
        let from_date = new Date(row.from_date_and_time);
        let to_date = new Date(row.to_date_and_time);

        let total_hours = (to_date - from_date) / (1000 * 60 * 60);
        let number_of_days = Math.ceil(total_hours / 24);

        frappe.db.get_single_value('Beams Accounts Settings', 'default_working_hours')
            .then(default_hours => {
                default_hours = parseFloat(default_hours) || 0;
                let ot_hours = Math.max(0, total_hours - default_hours);

                frappe.model.set_value(cdt, cdn, 'total_hours', total_hours.toFixed(2));
                frappe.model.set_value(cdt, cdn, 'ot_hours', ot_hours.toFixed(2));
                frappe.model.set_value(cdt, cdn, 'number_of_days', number_of_days);

                frm.refresh_field("work_details");
                setTimeout(() => {
                    calculate_daily_batta(frm, cdt, cdn);
                    calculate_ot_batta(frm, cdt, cdn);
                }, 200);
            });
    }
}

/* Calculate daily batta based on number of days and batta rate */
function calculate_daily_batta(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let total_hours = row.total_hours || 0;
    let number_of_days = Math.ceil(total_hours / 24);
    let daily_batta = number_of_days * (frm.doc.batta || 0);

    frappe.model.set_value(cdt, cdn, 'daily_batta', daily_batta);
    frm.refresh_field('work_details');
}

/* Calculate overtime batta based on OT hours and OT batta rate */
function calculate_ot_batta(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let ot_hours = row.ot_hours || 0;
    let ot_batta = ot_hours * (frm.doc.ot_batta || 0);

    frappe.model.set_value(cdt, cdn, 'ot_batta', ot_batta);
    frm.refresh_field('work_details');
}

/* Update daily batta for all work details rows */
function update_all_daily_batta(frm) {
    if (frm.doc.work_details) {
        frm.doc.work_details.forEach(row => {
            calculate_daily_batta(frm, row.doctype, row.name);
        });
        setTimeout(() => {
            frm.refresh_field('work_details');
            calculate_daily_batta(frm, cdt, cdn);
            calculate_ot_batta(frm, cdt, cdn);
        }, 200);

    }
}


/* Update OT batta for all work details rows */
function update_all_ot_batta(frm) {
    if (frm.doc.work_details) {
        frm.doc.work_details.forEach(row => {
            calculate_ot_batta(frm, row.doctype, row.name);
        });
        setTimeout(() => {
            frm.refresh_field('work_details');
        }, 200);
    }
}

/* Calculate total batta by summing daily batta values */
function calculate_batta(frm) {
    let total_batta = (frm.doc.daily_batta_with_overnight_stay || 0) +
                      (frm.doc.daily_batta_without_overnight_stay || 0);

    frappe.model.set_value(frm.doctype, frm.docname, 'batta', total_batta);
}

/* Calculate total food allowance and total batta for a row */
function calculate_total_food_allowance(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.total_food_allowance = (row.breakfast || 0) + (row.lunch || 0) + (row.dinner || 0);
    row.total_batta = row.total_food_allowance + (row.daily_batta || 0);

    frm.refresh_field("work_details");

    let total_batta_sum = frm.doc.work_details.reduce((sum, r) => sum + (r.total_batta || 0), 0);
    frm.set_value("total_daily_batta", total_batta_sum);
}

/* Calculate total distance travelled across all work details rows */
function calculate_total_distance_travelled(frm) {
    let total_distance = 0;
    frm.doc.work_details.forEach(row => {
        total_distance += row.distance_travelled_km || 0;
    });
    frm.set_value('total_distance_travelled_km', total_distance);
    frm.refresh_field("total_distance_travelled_km");
}

/* Calculate total hours from all work details rows */
function calculate_hours(frm) {
    let total_hours = 0;
    frm.doc.work_details.forEach(row => {
        total_hours += row.total_hours || 0;
    });
    frm.set_value('total_hours', total_hours);
    frm.refresh_field("total_hours");
}

/* Calculate total daily batta for all work details rows */
function calculate_total_daily_batta(frm) {
    let total_batta = 0;
    frm.doc.work_details.forEach(row => {
        total_batta += row.total_batta || 0;
    });
    frm.set_value('total_daily_batta', total_batta);
    frm.refresh_field("total_daily_batta");
}

/* Calculate total OT batta for all work details rows */
function calculate_total_ot_batta(frm) {
    let total_ot_batta = 0;
    frm.doc.work_details.forEach(row => {
        total_ot_batta += row.ot_batta || 0;
    });
    frm.set_value('total_ot_batta', total_ot_batta);
    frm.refresh_field("total_ot_batta");
}

/* Calculate total driver batta as the sum of total daily batta and total OT batta */
function calculate_total_driver_batta(frm) {
    let total_daily_batta = frm.doc.total_daily_batta || 0;
    let total_ot_batta = frm.doc.total_ot_batta || 0;

    frm.set_value('total_driver_batta', total_daily_batta + total_ot_batta);
    frm.refresh_field("total_driver_batta");
}


/* Determines eligibility for food allowance and updates fields accordingly.*/
function set_batta_for_food_allowance(frm, cdt, cdn) {
    let child = locals[cdt][cdn];

    let designation = "Driver";
    let is_overnight_stay = frm.doc.is_overnight_stay;

    let is_eligible = false;
    if (child.distance_travelled_km >= 50 && child.distance_travelled_km <= 100 && child.total_hours > 6) {
        is_eligible = true;
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
            method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.get_batta_for_food_allowance",
            args: {
                designation: designation,
                from_date_time: child.from_date_and_time,
                to_date_time: child.to_date_and_time,
                total_hrs: child.total_hours,
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

function calculate_allowance(frm) {
    if (!frm.doc.supplier.length) {
        frappe.msgprint(__("Please select a supplier."));
        return;
    }

    frappe.call({
        method: "beams.beams.doctype.bureau_trip_sheet.bureau_trip_sheet.calculate_batta_allowance",
        args: {
            designation: frm.doc.designation,
            is_travelling_outside_kerala: frm.doc.is_travelling_outside_kerala || 0,
            is_overnight_stay: frm.doc.is_overnight_stay || 0,
            total_distance_travelled_km: frm.doc.total_distance_travelled_km || 0,
            total_hours: frm.doc.total_hours || 0
        },
        callback: function(r) {
            if (r.message) {
                frm.set_value("daily_batta_with_overnight_stay", r.message.daily_batta_with_overnight_stay);
                frm.set_value("daily_batta_without_overnight_stay", r.message.daily_batta_without_overnight_stay);
                frm.set_value("batta", r.message.batta);
            }
        }
    });
}
