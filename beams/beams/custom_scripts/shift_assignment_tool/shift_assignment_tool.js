frappe.ui.form.on('Shift Assignment Tool', {
	onload: function(frm) {
		if (!frm.doc.department || !frm.doc.company) {
			frappe.db.get_value('Employee', {'user_id': frappe.session.user}, ['department', 'company'])
				.then(r => {
					let values = r.message;
					if (values) {
						if (!frm.doc.department && values.department) {
							frm.set_value('department', values.department);
						}
						if (!frm.doc.company && values.company) {
							frm.set_value('company', values.company);
						}
					}
				});
		}
	},
	start_date: function(frm) {
		if (frm.doc.start_date) {
			frm.set_value('end_date', frm.doc.start_date);
		}
	}
});
