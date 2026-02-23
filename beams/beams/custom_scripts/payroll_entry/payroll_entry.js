frappe.ui.form.on('Payroll Entry', {
	refresh: function(frm) {
		if (frm.is_new() && frm.doc.posting_date && frm.doc.payroll_frequency === 'Monthly' && !frm.__dates_set_by_beams) {
			set_previous_month_dates(frm);
			frm.__dates_set_by_beams = true;
		}
	},

	posting_date: function(frm) {
		set_previous_month_dates(frm);
	},

	payroll_frequency: function(frm) {
		set_previous_month_dates(frm);
	}
});

/**
* Set the start and end dates to cover the previous month
* relative to the selected `posting_date`.
*/
function set_previous_month_dates(frm) {
	if (!frm.doc.posting_date || frm.doc.payroll_frequency !== 'Monthly') {
		return;
	}

	let posting_date = frappe.datetime.str_to_obj(frm.doc.posting_date);
	if (!posting_date) {
		return;
	}

	let prev_year = posting_date.getFullYear();
	let prev_month = posting_date.getMonth() - 1;

	if (prev_month < 0) {
		prev_month = 11;
		prev_year = prev_year - 1;
	}

	let start_date = new Date(prev_year, prev_month, 1);
	let end_date = new Date(prev_year, prev_month + 1, 0);
	let start_date_formatted = frappe.datetime.obj_to_str(start_date);
	let end_date_formatted = frappe.datetime.obj_to_str(end_date);

	if (frm.doc.start_date !== start_date_formatted) {
		frm.doc.start_date = start_date_formatted;
		frm.refresh_field('start_date');
	}

	if (frm.doc.end_date !== end_date_formatted) {
		frm.doc.end_date = end_date_formatted;
		frm.refresh_field('end_date');
	}
}
