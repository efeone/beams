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
    onload: function(frm) {
       set_employee_exit_clearance_filter(frm)
    },
    employee: function(frm) {
        set_employee_exit_clearance_filter(frm);
    }
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

/**
 * Sets a filter on the `employee_exit_clearance` Link field in the
 * `employee_clearance` child table to show only records that match
 * the selected department (from the row) and employee (from the parent form).
 */
function set_employee_exit_clearance_filter(frm) {
    frm.fields_dict['employee_clearance'].grid.get_field('employee_exit_clearance').get_query = function (doc, cdt, cdn) {
        const child = locals[cdt][cdn];
        return {
            filters: {
                employee: frm.doc.employee,
                clearance_for_department: child.department
            }
        };
    };
}
