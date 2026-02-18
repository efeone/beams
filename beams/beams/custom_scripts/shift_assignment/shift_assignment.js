frappe.ui.form.on('Shift Assignment', {
	start_date: function(frm) {
		if (frm.doc.start_date) {
			frm.set_value('end_date', frm.doc.start_date);
		}
	}
});
