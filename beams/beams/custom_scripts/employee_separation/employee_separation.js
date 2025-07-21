frappe.ui.form.on('Employee Separation', {
	refresh: function(frm) {
		apply_template_filter(frm);
	},

	department: function(frm) {
		apply_template_filter(frm);
	},

	designation: function(frm) {
		apply_template_filter(frm);
	},
});

function apply_template_filter(frm) {
	if (frm.doc.department && frm.doc.designation) {
		frm.set_query("employee_separation_template", function () {
			return {
				filters: {
					department: frm.doc.department,
					designation: frm.doc.designation
				}
			};
		});
	}
}
