// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Interview Tool', {
	onload(frm) {
		frm.set_value('date', frappe.datetime.get_today());
		frm.toggle_display('job_applicants', false);
	},
	from_time: function (frm) {
		validate_time_range(frm);
	},
	to_time: function (frm) {
		validate_time_range(frm);
	},
	refresh: function (frm) {
		frm.disable_save()
		frm.set_value('interview_round', '');
		frm.set_value('scheduled_on', '');
		frm.set_value('from_time', '');
		frm.set_value('to_time', '');
		frm.clear_table('job_applicants');
		frm.refresh_field('job_applicants');
		frm.toggle_display('job_applicants', false);
		if (frm.fields_dict.applicant_status) {
			frm.fields_dict.applicant_status.$input.on('change', function() {
				if (frm.fields_dict.get_btn) {
					frm.fields_dict.get_btn.click();
				}
			});
		}

		// Button to fetch job applicants
		let get_btn = frm.add_custom_button('Get Job Applicants', function () {
			const filters = {};

			if (frm.doc.job_opening) {
				filters.job_title = frm.doc.job_opening;
			}
			if (frm.doc.department) {
				filters.department = frm.doc.department;
			}
			if (frm.doc.designation) {
				filters.designation = frm.doc.designation;
			}
			if (frm.doc.applicant_status) {
				filters.status = frm.doc.applicant_status;
			}


			frappe.call({
				method: 'beams.beams.doctype.employee_interview_tool.employee_interview_tool.fetch_filtered_job_applicants',
				args: { filters },
				callback: function (r) {
					if (!r.exc) {
						frm.clear_table('job_applicants');
						(r.message || []).forEach(function (app) {
							let row = frm.add_child('job_applicants');
							row.job_applicant = app.name;
							row.applicant_name = app.applicant_name;
							row.status = app.status;
							row.designation = app.designation;
						});
						frm.refresh_field('job_applicants');
						frm.toggle_display('job_applicants', true);
						get_btn.removeClass('btn-primary').addClass('btn-default');

						// Button to create interview
						let create_interview_btn = frm.add_custom_button('Create Interview', function () {
							let selected_rows = frm.fields_dict.job_applicants.grid.get_selected_children();

							if (!selected_rows.length) {
								frappe.msgprint(__('Please select one or more rows in the Job Applicants table.'));
								return;
							}
							let missing_fields = [];
							if (!frm.doc.interview_round) missing_fields.push(__('Interview Round'));
							if (!frm.doc.scheduled_on) missing_fields.push(__('Scheduled On'));
							if (!frm.doc.from_time) missing_fields.push(__('From Time'));
							if (!frm.doc.to_time) missing_fields.push(__('To Time'));

							if (missing_fields.length) {
								frappe.msgprint({
									title: __('Missing Required Scheduling Fields'),
									message: __('Please ensure the following fields are filled:') +
										'<br><b>' + missing_fields.join(', ') + '</b>',
									indicator: 'orange'
								});
								return;
							}

							frappe.call({
								method: 'beams.beams.doctype.employee_interview_tool.employee_interview_tool.create_bulk_interviews',
								args: {
									applicants: selected_rows.map(row => ({
										job_applicant: row.job_applicant,
										applicant_name: row.applicant_name,
										designation: row.designation,
										interview_round: frm.doc.interview_round,
										scheduled_on: frm.doc.scheduled_on,
										from_time: frm.doc.from_time,
										to_time: frm.doc.to_time
									}))
								},
								callback: function (r) {
									if (!r.exc) {
										const data = r.message || {};
										let any_message = false;
										// Show success if interviews were created
										if (Array.isArray(data.created) && data.created.length > 0) {
											const created_ids = data.created.map(c => c.job_applicant).join(', ');
											frappe.msgprint(__('Interviews created successfully for: ') + created_ids);
										}
										// Show warning if some were skipped
										if (Array.isArray(data.skipped_applicants) && data.skipped_applicants.length > 0) {
											frappe.msgprint({
												title: __('Note'),
												message: __('Interviews already exist for the following applicants: ') + data.skipped_applicants.join(', '),
												indicator: 'orange'
											});
										}
									}
								}
							});
						});
						create_interview_btn.removeClass('btn-default').addClass('btn-primary');

						// Button to create local enquiry report
						let create_ler_btn = frm.add_custom_button('Create Local Enquiry Report', function () {
							let selected_rows = frm.fields_dict.job_applicants.grid.get_selected_children();

							if (!selected_rows.length) {
								frappe.msgprint(__('Please select one or more rows in the Job Applicants table.'));
								return;
							}

							frappe.call({
								method: 'beams.beams.doctype.employee_interview_tool.employee_interview_tool.create_bulk_ler',
								args: {
									applicants: selected_rows.map(row => ({
										job_applicant: row.job_applicant,
										applicant_name: row.applicant_name,
									}))
								},
								callback: function (r) {
									if (!r.exc) {
										const data = r.message || {};
										if (Array.isArray(data.created) && data.created.length > 0) {
											let created_ids = data.created.map(c => c.job_applicant).join(', ');
											frappe.msgprint(__('Local Enquiry Report created successfully for: ') + created_ids);
										}
										if (Array.isArray(data.skipped_applicants) && data.skipped_applicants.length > 0) {
											frappe.msgprint({
												title: __('Note'),
												message: __('Local Enquiry Report already exists for: ') + data.skipped_applicants.join(', '),
												indicator: 'orange'
											});
										}
									}
								}
							});
						});
						create_ler_btn.removeClass('btn-default').addClass('btn-primary');
					}
				}
			});
		});
		get_btn.removeClass('btn-default').addClass('btn-primary');
	}
});

/**
 * Validates that the "From Time" is earlier than the "To Time" in the form.
 */
function validate_time_range(frm) {
	if (frm.doc.from_time && frm.doc.to_time) {
		if (frm.doc.from_time >= frm.doc.to_time) {
			frappe.throw({
				title: __('Invalid Time Range'),
				message: __('The <b>From Time</b> must be earlier than the <b>To Time</b>. Please correct the time range.')
			});
		}
	}
}