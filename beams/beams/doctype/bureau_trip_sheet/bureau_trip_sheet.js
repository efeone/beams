// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Details', {
    from_date_and_time: function (frm, cdt, cdn) {
        calculate_hours_and_days(frm, cdt, cdn);
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
        }

        calculate_hours_and_days(frm, cdt, cdn);
    },
    total_hours: function (frm, cdt, cdn) {
        calculate_daily_batta(frm, cdt, cdn);
        calculate_ot_batta(frm, cdt, cdn);
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
    },
    work_details_add:  function(frm, cdt, cdn) {
        calculate_total_distance_travelled(frm, cdt, cdn);
        calculate_hours(frm, cdt, cdn);
        calculate_total_daily_batta(frm, cdt, cdn);
        calculate_total_ot_batta(frm, cdt, cdn);
    },
    work_details_remove: function(frm, cdt, cdn) {
        calculate_total_distance_travelled(frm, cdt, cdn);
        calculate_hours(frm, cdt, cdn);
        calculate_total_daily_batta(frm, cdt, cdn);
        calculate_total_ot_batta(frm, cdt, cdn);
    },
    total_hours: function(frm, cdt, cdn) {
        calculate_hours(frm, cdt, cdn);
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
        calculate_daily_batta(frm);
    },
    is_travelling_outside_kerala: function (frm) {
        calculate_daily_batta(frm);
    }

});
/* set filter is transporter in Supplier. */
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

    // Bureau Trip Sheet Doctype-ile total_daily_batta update cheyyan
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
    frm.set_value('total_hours', totalHours);
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
