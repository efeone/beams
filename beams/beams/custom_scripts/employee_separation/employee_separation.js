// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Separation', {
	refresh: function(frm) {
		apply_template_filter(frm);
		apply_employee_field_visibility(frm);
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
	},
	boarding_begins_on: function(frm){
		set_notice_period_end_date(frm);
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

/**
 * Apply field visibility rules for Employee Separation based on user roles.
 *
 * This function:
 * 1. Determines whether the logged-in user has ONLY the default employee roles.
 * 2. If YES → Shows only selected fields (employee view).
 * 3. If NO → Shows all fields (HOD / HR / Admin view).
 */
function apply_employee_field_visibility(frm){
		const roles = frappe.user_roles || [];
		const default_employee_roles = ["Employee", "All", "Guest", "Desk User"];

		const has_only_employee_roles =
			roles.every(r => default_employee_roles.includes(r)) &&
			roles.length === default_employee_roles.length;

		const allowed_fields = [
			"employee",
			"boarding_begins_on",
			"remarks",
			"notice_period_end_date",
			"employee_name",
			"department",
			"designation",
			"employee_grade"
		];

		frm.fields.forEach(f => {
			frm.toggle_display(f.df.fieldname, true);
			frm.toggle_enable(f.df.fieldname, true);
		});

		if (has_only_employee_roles) {
			frm.fields.forEach(f => {
				const fn = f.df.fieldname;
				if (!allowed_fields.includes(fn)) {
					frm.toggle_display(fn, false);
					frm.toggle_enable(fn, false);
				}
			});
		}
}

/**
 * Calculate notice period end date = boarding_begins_on + employee.notice_number_of_days
 */
function set_notice_period_end_date(frm) {
	if(!frm.doc.employee || !frm.doc.boarding_begins_on) return;

	frappe.db.get_value("Employee", frm.doc.employee, "notice_number_of_days")
		.then(res => {
			const days = res.message.notice_number_of_days || 0;
			const end_days = frappe.datetime.add_days(frm.doc.boarding_begins_on, days);
			frm.set_value("notice_period_end_date", end_days)
		})
}
