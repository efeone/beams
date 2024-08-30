// // Copyright (c) 2024, efeone and contributors
// // For license information, please see license.txt

frappe.ui.form.on('Driver Batta Claim', {
    onload: function (frm) {
        calculate_totals(frm);
    },
    refresh: function (frm) {
        frm.set_query('driver', function() {
              return {
                  filters: {
                      'is_internal': 0
                  }
              };
          });
        calculate_totals(frm);
    },
});

frappe.ui.form.on('Work Details', {
    from_date_and_time: function (frm, cdt, cdn) {
        validate_dates_and_calculate(frm, cdt, cdn);
    },
    to_date_and_time: function (frm, cdt, cdn) {
        validate_dates_and_calculate(frm, cdt, cdn);
    }
});

/* function to validate dates and perform calculations*/
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

        // Validation: Ensure the same date range is not duplicated in multiple rows
        let overlap_found = false;
        frm.doc.work_detials.forEach(other_row => {
            if (other_row.name !== row.name) {
                if (other_row.from_date_and_time && other_row.to_date_and_time) {
                    let other_from_time = new Date(other_row.from_date_and_time);
                    let other_to_time = new Date(other_row.to_date_and_time);

                    if (
                        (from_time >= other_from_time && from_time <= other_to_time) ||
                        (to_time >= other_from_time && to_time <= other_to_time)
                    ) {
                        overlap_found = true;
                    }
                }
            }
        });

        if (overlap_found) {
            frappe.msgprint(__('The date range overlaps with another entry'));
            frappe.model.set_value(cdt, cdn, 'from_date_and_time', '');
            frappe.model.set_value(cdt, cdn, 'to_date_and_time', '');
            return;
        }

        calculate_hours_and_totals(frm, cdt, cdn);
    }
}

/* Function to calculate hours and batta*/
function calculate_hours_and_totals(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.from_date_and_time && row.to_date_and_time) {
        let from_time = new Date(row.from_date_and_time);
        let to_time = new Date(row.to_date_and_time);
        let diff = (to_time - from_time) / (1000 * 60 * 60);

        if (diff >= 0) {
            frappe.db.get_single_value('Beams Accounts Settings', 'default_working_hours')
                .then(default_working_hours => {
                    row.total_hours = diff;
                    row.ot_hours = diff > default_working_hours ? diff - default_working_hours : 0;

                    row.daily_batta = (row.total_hours - row.ot_hours) * frm.doc.daily_batta;
                    row.ot_batta = row.ot_hours * frm.doc.ot_bata;

                    frm.refresh_field('work_detials');
                    calculate_totals(frm);
                });
        }
    }
}

/*Function to calculate total batta values*/
function calculate_totals(frm) {
    let total_daily_batta = 0;
    let total_ot_batta = 0;

    (frm.doc.work_detials || []).forEach(row => {
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
