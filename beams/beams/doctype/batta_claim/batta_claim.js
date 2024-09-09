

// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Batta Claim', {
    onload: function (frm) {
        set_batta_based_on_options(frm)
        calculate_totals(frm);
    },
    refresh: function (frm) {
        set_batta_based_on_options(frm)
        calculate_totals(frm);
    },
    batta_type: function(frm) {
        set_batta_based_on_options(frm)
        frm.doc.work_detail.forEach(function(row) {
            frappe.model.set_value(row.doctype, row.name, 'batta_type', frm.doc.batta_type);
        });
        frm.refresh_field('work_detail');
    }
});

frappe.ui.form.on('Work Detail', {
    from_date_and_time: function (frm, cdt, cdn) {
        validate_dates_and_calculate(frm, cdt, cdn);
    },
    to_date_and_time: function (frm, cdt, cdn) {
        validate_dates_and_calculate(frm, cdt, cdn);
    }
});



/* Function to set options for Batta Based On field based on Batta Type */
function set_batta_based_on_options(frm) {
    if (frm.doc.batta_type === 'External') {
        frm.set_df_property('batta_based_on', 'options', 'Hours');
        frm.set_value('batta_based_on', 'Hours');
    } else {
        frm.set_df_property('batta_based_on', 'options', ['Daily', 'Hours']);
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
                        // row.number_of_days = 1;
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
    let total_daily_batta = 0;
    let total_ot_batta = 0;

    (frm.doc.work_detail || []).forEach(row => {
        total_daily_batta += row.daily_batta || 0;
        total_ot_batta += row.ot_batta || 0;
    });

    let total_driver_batta = total_daily_batta + total_ot_batta;

    frm.set_value({
        'total_daily_batta': total_daily_batta,
        'total_ot_batta': total_ot_batta,
        'total_driver_batta': total_driver_batta
    });

    frm.refresh_field(['total_daily_batta', 'total_ot_batta', 'total_driver_batta']);
}
