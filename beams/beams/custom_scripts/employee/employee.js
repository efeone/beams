frappe.ui.form.on('Employee', {
	/**
	* Adds a custom button 'Training Request' for users with 'HOD' role
	* This button creates a new 'Training Request' document.
	*/
	job_applicant: function (frm) {
		if (frm.doc.job_applicant) {
			// Fetch Job Applicant data using frappe.db.get_doc
			frappe.db.get_doc('Job Applicant', frm.doc.job_applicant)
			.then(job_applicant => {
				// Map fields from Job Applicant to Employee
				frm.set_value('first_name', job_applicant.applicant_name);
				frm.set_value('date_of_birth', job_applicant.date_of_birth);
				frm.set_value('gender', job_applicant.gender);
				frm.set_value('cell_number', job_applicant.phone_number);
				frm.set_value('name_of_father', job_applicant.father_name);
				frm.set_value('designation', job_applicant.designation);
				frm.set_value('department', job_applicant.department);
				frm.set_value('current_address', job_applicant.current_address);
				frm.set_value('permanent_address', job_applicant.permanent_address);
				frm.set_value('marital_status', job_applicant.marital_status);
				frm.set_value('aadhar_id', job_applicant.aadhar_number);


				frm.refresh_fields();
			});
		}
		get_appointment_date(frm, frm.doc.job_applicant)
	},
	reports_to: function(frm) {
		if (frm.doc.reports_to) {
			frappe.db.get_value('Employee', frm.doc.reports_to, 'user_id')
			.then(r => {
				if (r.message.user_id) {
					reports_to_user = r.message.user_id
					frm.set_value('expense_approver', reports_to_user);
					frm.set_value('shift_request_approver', reports_to_user);
					frm.set_value('leave_approver', reports_to_user);
				}
			})
		}
		else {
			// Clear approver fields if 'reports_to' is empty
			frm.set_value('expense_approver', '');
			frm.set_value('shift_request_approver', '');
			frm.set_value('leave_approver', '');
		}
	},
	refresh: function(frm){
		if (!frm.is_new() && frappe.user.has_role('HR Manager')) { // Adds the custom button 'Training Request' in the 'Create' section
			// Check if employee name exists for the logged-in user and add 'Event' button if available
			frappe.call(		{
				method: "beams.beams.custom_scripts.employee.employee.get_employee_name_for_user",
				args: {
					user_id: frappe.session.user
				},
				callback: function(response) {
					if (response.message) {
						frm.add_custom_button(__('Event'), function() {
							frappe.model.open_mapped_doc({
								method: "beams.beams.custom_scripts.employee.employee.create_event",
								frm: frm,
								args: {
									"employee_id": frm.doc.name,
									"hod_user": frappe.session.user
								}
							});
						}, __('Create'));

						frm.add_custom_button('Training Request', function() {
							// Call the server-side function to fetch the employee ID for the current user
							frappe.call({
								method: "beams.beams.custom_scripts.employee.employee.get_employee_name_for_user",
								args: {
									user_id: frappe.session.user
								},
								callback: function(response) {
									if (response.message) {
										// If employee ID is found, create a new 'Training Request' document
										frappe.new_doc('Training Request', {
											employee: frm.doc.name,
											training_requested_by: response.message // Set training_requested_by to the fetched employee ID
										});
									} else {

										// Show a message if no employee record is found for the user
										frappe.msgprint(__('No employee record found for the current user.'));
									}
								}
							});
						}, 'Create');
					}
				}
			});
		}
	},
	employment_type: function(frm) {
		frappe.call({
			method: "beams.beams.custom_scripts.employee.employee.get_notice_period",
			args: {
				employment_type: frm.doc.employment_type,
				job_applicant: frm.doc.job_applicant
			},
			callback: function(response) {
				if (response.message !== undefined && response.message !== null) {
					// Update the notice period if it's different or currently None/empty
					if (response.message !== frm.doc.notice_number_of_days) {
						frm.set_value('notice_number_of_days', response.message);
						frm.refresh_field('notice_number_of_days');
					}
				}
			},

		});
	}
});

/**
 *  Set 'Date of Appointment' from Appointment Letter
 *  based on selected Job Applicant.
 */
function get_appointment_date(frm, job_applicant) {
	if (job_applicant) {
		frappe.db.get_value('Appointment Letter', { job_applicant: job_applicant }, 'appointment_date')
			.then(r => {
				if (r.message && r.message.appointment_date) {
					frm.set_value('date_of_appointment', r.message.appointment_date);
				} else {
					frm.set_value('date_of_appointment', '');
				}
			});
	} else {
		frm.set_value('date_of_appointment', '');
	}
}
