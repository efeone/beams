// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

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

/**
 * Added filters in employee separation template based on employee designation and department
*/

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
