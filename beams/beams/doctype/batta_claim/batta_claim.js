frappe.ui.form.on('Batta Claim', {
    onload: function (frm) {
        set_batta_based_on_options(frm);
        calculate_totals(frm);
        calculate_batta_totals(frm);
    },
    room_rent_batta: function(frm) {
       calculate_batta_totals(frm);
   },
   daily_batta_with_overnight_stay: function(frm) {
       calculate_batta_totals(frm);
   },
   daily_batta_without_overnight_stay: function(frm) {
       calculate_batta_totals(frm);
   },
   food_allowance: function(frm) {
       calculate_batta_totals(frm);
   },
    origin: function(frm) {
        update_work_detail(frm);
    },
    destination: function(frm) {
        update_work_detail(frm);
    },
    work_detail_add: function(frm, cdt, cdn) {
       calculate_total_distance_travelled(frm);
   },
    work_detail_onform_render: function(frm, cdt, cdn) {
      calculate_total_distance_travelled(frm);
   },
    work_detail_remove: function(frm, cdt, cdn) {
       calculate_total_distance_travelled(frm);
   },
    refresh: function (frm) {
        set_batta_based_on_options(frm);
        calculate_totals(frm);
        calculate_total_distance_travelled(frm);
        calculate_batta_totals(frm);
    },
    batta_type: function(frm) {
        set_batta_based_on_options(frm);
        frm.doc.work_detail.forEach(function(row) {
            frappe.model.set_value(row.doctype, row.name, 'batta_type', frm.doc.batta_type);
        });
        frm.refresh_field('work_detail');
        set_batta_based_on_options(frm);
        handle_designation_based_on_batta_type(frm);
    },
    employee: function (frm) {
        handle_designation_based_on_batta_type(frm);
    },
    batta: function (frm) {
        // Loop through each row in the work_detail child table to calculate the row values based on the updated batta
        frm.doc.work_detail.forEach(function(row) {
            if (frm.doc.batta_based_on === 'Daily') {
                row.number_of_days = Math.ceil(row.total_hours / 24);
                row.daily_batta = row.number_of_days * frm.doc.batta;
            } else if (frm.doc.batta_based_on === 'Hours') {
                row.daily_batta = (row.total_hours - row.ot_hours) * frm.doc.batta;
            }

            row.ot_batta = row.ot_hours * frm.doc.ot_batta;

            // Refresh the fields for each row in the child table
            frm.refresh_field('work_detail');
        });
        // After updating all the rows, recalculate the total values
        calculate_totals(frm);
    }
});

frappe.ui.form.on('Work Detail', {
    from_date_and_time: function (frm, cdt, cdn) {
        validate_dates_and_calculate(frm, cdt, cdn);
    },
    to_date_and_time: function (frm, cdt, cdn) {
        validate_dates_and_calculate(frm, cdt, cdn);
    },
    origin: function(frm) {
        update_work_detail(frm);
    },
    destination: function(frm) {
        update_work_detail(frm);
    }
});

/* Function to set options for Batta Based On field based on Batta Type */
function set_batta_based_on_options(frm) {
    if (frm.doc.batta_type === 'External') {
        frm.set_df_property('batta_based_on', 'options', 'Hours');
        frm.set_value('batta_based_on', 'Hours');
    } else {
        frm.set_df_property('batta_based_on', 'options', ['Daily']);
        frm.set_value('batta_based_on', 'Daily');
    }
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
        // Clear designation for External
    } else if (frm.doc.batta_type === 'External') {
        frm.set_value('designation', '');
    }
}


/* Function to validate dates and perform calculations */
function validate_dates_and_calculate(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.from_date_and_time && row.to_date_and_time) {
        let from_time = new Date(row.from_date_and_time);
        let to_time = new Date(row.to_date_and_time);

        // Validation: From date should not be greater than to date
        if (from_time > to_time) {
            frappe.msgprint(__('From Date and Time cannot be greater than To Date and Time'));
            frappe.model.set_value(cdt, cdn, 'to_date_and_time', '');
            return;
        }
        calculate_hours_and_totals(frm, cdt, cdn);
    }
}

/* Function to calculate hours and batta */
function calculate_hours_and_totals(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.from_date_and_time && row.to_date_and_time) {
        let from_time = new Date(row.from_date_and_time);
        let to_time = new Date(row.to_date_and_time);
        let diff = (to_time - from_time) / (1000 * 60 * 60); // Difference in hours

        if (diff >= 0) {
            frappe.db.get_single_value('Beams Accounts Settings', 'default_working_hours')
              .then(default_working_hours => {
                    row.total_hours = diff;
                    row.ot_hours = diff > default_working_hours ? diff - default_working_hours : 0;

                    if (frm.doc.batta_based_on === 'Daily') {
                        row.number_of_days = Math.ceil(row.total_hours / 24);
                        row.daily_batta = row.number_of_days * frm.doc.batta;
                    } else if (frm.doc.batta_based_on === 'Hours') {
                        row.daily_batta = (row.total_hours - row.ot_hours) * frm.doc.batta;
                    }

                    row.ot_batta = row.ot_hours * frm.doc.ot_batta;

                    frm.refresh_field('work_detail');
                    calculate_totals(frm);
                });
        }
    }
}

/* Function to calculate total batta values */
function calculate_totals(frm) {
    frm.call({
        method: "calculate_total_batta",
        doc: frm.doc,
        callback: function(response) {
            // Update the form fields with the calculated totals
            frm.set_value({
                'total_daily_batta': response.message.total_daily_batta,
                'total_ot_batta': response.message.total_ot_batta,
                'total_driver_batta': response.message.total_driver_batta
            });

            // Refresh the fields to update totals
            frm.refresh_field(['total_daily_batta', 'total_ot_batta', 'total_driver_batta']);
        }
    });
}

/* Function to calculate batta values */
function calculate_batta_totals(frm) {
    frm.call({
        method: "calculate_batta",  // Replace with actual path to the Python function
        doc: frm.doc,
        callback: function(response) {
            // Update the form fields with the calculated totals from the Python method
            frm.set_value({
                'room_rent_batta': response.message.room_rent_batta,
                'daily_batta_with_overnight_stay': response.message.daily_batta_with_overnight_stay,
                'daily_batta_without_overnight_stay': response.message.daily_batta_without_overnight_stay,
                'food_allowance': response.message.food_allowance,
                'batta': response.message.batta  // Assuming 'batta' is the total batta field
            });

            // Refresh the fields to display updated totals
            frm.refresh_field(['room_rent_batta', 'daily_batta_with_overnight_stay', 'daily_batta_without_overnight_stay', 'food_allowance', 'batta']);
        }
    });
}


frappe.ui.form.on('Work Detail', {
    distance_travelled_km: function(frm, cdt, cdn) {
        calculate_total_distance_travelled(frm);
    },

    work_detail_add: function(frm, cdt, cdn) {
        const { origin, destination } = frm.doc;

           // Set initial values for the new row
        frappe.model.set_value(cdt, cdn, 'origin', origin);
        frappe.model.set_value(cdt, cdn, 'destination', destination);
    }
});

function calculate_total_distance_travelled(frm) {
    let totalDistance = 0;
       // Sum all distance_travelled_km from the Work Detail child table
    frm.doc.work_detail.forEach(function(row) {
        if (row.distance_travelled_km) {
            totalDistance += row.distance_travelled_km;
        }
    });
       // Set the total_distance_travelled_km field with the calculated sum
    frm.set_value('total_distance_travelled_km', totalDistance);
}

function update_work_detail(frm) {
    const { origin, destination, work_detail } = frm.doc;

    // Update existing child rows with parent values
    work_detail.forEach((row, index) => {
        if (index >= 0) {
            if (!row.origin || !row.destination) {
                frappe.model.set_value(row.doctype, row.name, 'origin', origin);
                frappe.model.set_value(row.doctype, row.name, 'destination', destination);
            }
        }
    });

    frm.refresh_field('work_detail');
}

frappe.ui.form.on('Batta Claim', {
    designation: function(frm) {
        frm.trigger('calculate_batta');
    },
    is_travelling_outside_kerala: function(frm) {
        frm.trigger('calculate_batta');
    },
    is_overnight_stay: function(frm) {
        frm.trigger('calculate_batta');
    },
    total_distance_travelled_km: function(frm) {
        frm.trigger('calculate_batta');
    },

    calculate_batta: function(frm) {
        // Ensure designation and total distance are filled before calling the function
        if (frm.doc.designation && frm.doc.total_distance_travelled_km) {
            // Sum up total_hours from the work_detail child table
            let total_hours = 0;
            if (frm.doc.work_detail) {
                frm.doc.work_detail.forEach(row => {
                    total_hours += row.total_hours || 0;
                });
            }

            frappe.call({
                method: "beams.beams.doctype.batta_claim.batta_claim.calculate_batta_allowance",
                args: {
                    designation: frm.doc.designation,
                    is_travelling_outside_kerala: frm.doc.is_travelling_outside_kerala,
                    is_overnight_stay: frm.doc.is_overnight_stay,
                    total_distance_travelled_km: frm.doc.total_distance_travelled_km,
                    total_hours: total_hours,
                },
                callback: function(r) {
                    if (r.message) {
                        // Set batta values in the form
                        frm.set_value('batta', r.message.batta);
                        frm.set_value('room_rent_batta', r.message.room_rent_batta);
                        frm.set_value('daily_batta_with_overnight_stay', r.message.daily_batta_with_overnight_stay);
                        frm.set_value('daily_batta_without_overnight_stay', r.message.daily_batta_without_overnight_stay);
                        frm.set_value('food_allowance', r.message.food_allowance);
                    }
                }
            });
        }
    }
});
