// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Substitute Booking", {
	daily_wage: function(frm) {
			calculate_total_wage(frm);
	}
});

frappe.ui.form.on('Substitution Bill Date', {
    date: function(frm, cdt, cdn) {
        // Validate dates and update no_of_days when a date is entered or changed
        validate_dates(frm);
    }
});

function validate_dates(frm) {
    let dates = frm.doc.substitution_bill_date.map(row => row.date).filter(date => date);

    // Check for duplicate dates
    let unique_dates = [...new Set(dates)];
    if (unique_dates.length !== dates.length) {
        frappe.msgprint({
            title: __('Message'),
            message: __('Dates should be unique.'),
            indicator: 'red'
        });
        frm.refresh_field('substitution_bill_date');
        return;
    }

    let unique_dates_count = unique_dates.length;
    frm.set_value('no_of_days', unique_dates_count);

    // Calculate the total wage after updating no_of_days
    calculate_total_wage(frm);
}

function calculate_total_wage(frm) {
    let no_of_days = frm.doc.no_of_days;
    let daily_wage = frm.doc.daily_wage;

    if (no_of_days && daily_wage) {
        // Calculate total wage
        let total_wage = no_of_days * daily_wage;
        frm.set_value('total_wage', total_wage);
    }
}
