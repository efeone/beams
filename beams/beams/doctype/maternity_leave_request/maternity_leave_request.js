// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maternity Leave Request', {
		setup: function (frm) {
				// Set filter for employee field to only show Female employees
				frm.set_query('employee', function () {
						return {
								filters: {
										gender: 'Female'
								}
						};
				});
		},

		onload: function (frm) {
				// Fetch Maternity Leave Type from HR Settings and set it to the leave_type field
				frappe.db.get_doc('Beams HR Settings').then(hr_settings => {
						if (hr_settings && hr_settings.maternity_leave_type) {
								frm.set_value('leave_type', hr_settings.maternity_leave_type);
						}
				});
		},

		validate: function(frm) {
				// Check if Maternity Leave Type is set in the Beams HR Settings
				frappe.db.get_doc('Beams HR Settings').then(hr_settings => {
						if (!hr_settings || !hr_settings.maternity_leave_type) {
								frappe.msgprint(__('Maternity Leave Type is not set in HR Settings. Please configure it to proceed.'), 'Validation Error', 'red');
								frappe.validated = false; // Prevent saving the form
						}
				});

				// Validate birth_count to be greater than 0
				if (frm.doc.birth_count <= 0) {
						frappe.msgprint(__('Birth count must be greater than 0.'), 'Validation Error', 'red');
						frappe.validated = false; 
				} else {
						// Check the value of birth_count and set no_of_days accordingly
						if (frm.doc.birth_count === 1 || frm.doc.birth_count === 2) {
								frm.set_value('no_of_days', 180);
						} else if (frm.doc.birth_count >= 3) {
								frm.set_value('no_of_days', 90);
						}
				}
		}
});
