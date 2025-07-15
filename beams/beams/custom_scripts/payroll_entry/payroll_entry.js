frappe.ui.form.on('Payroll Entry', {
	refresh: function(frm) {
		set_previous_month_dates(frm);
	},
	
	posting_date: function(frm) {
		set_previous_month_dates(frm);
	},
	
	onload: function(frm) {
		setTimeout(() => {
			set_previous_month_dates(frm);
		}, 500);
	}
});

function set_previous_month_dates(frm) {
	/**
	* Set the start and end dates to cover the previous month
	* relative to the selected `posting_date`.
	*/
	if (!frm.doc.posting_date) {
		return;
	}
	
	let posting_date = frappe.datetime.str_to_obj(frm.doc.posting_date);
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
		frm.set_value('start_date', start_date_formatted);
	}
	
	if (frm.doc.end_date !== end_date_formatted) {
		frm.set_value('end_date', end_date_formatted);
	}
}