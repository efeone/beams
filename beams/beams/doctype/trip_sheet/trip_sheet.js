// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on('Trip Sheet', {
    starting_date_and_time: function(frm) {
        frm.call({
            method: "validate_start_datetime_and_end_datetime",
            doc: frm.doc,
        });
    },
    ending_date_and_time: function(frm) {
        frm.call({
            method: "validate_start_datetime_and_end_datetime",
            doc: frm.doc,
        });
    },
    vehicle: function(frm) {
        if (frm.doc.vehicle) {
            frappe.call({
                method: "beams.beams.doctype.trip_sheet.trip_sheet.get_last_odometer",
                args: {
                    vehicle: frm.doc.vehicle
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("initial_odometer_reading", r.message);
                    } else {
                        frm.set_value("initial_odometer_reading", 0);
                    }
                }
            });
        } else {
            frm.set_value("initial_odometer_reading", null);
        }
    }
});
