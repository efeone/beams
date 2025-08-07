frappe.ui.form.on('Job Applicant', {
	refresh: function (frm) {
		frm.remove_custom_button(__('Interview'), __('Create'));
		handle_custom_buttons(frm);
		frm.toggle_display('applicant_interview_rounds', !frm.is_new());
		const statuses = [
			'Document Uploaded', 'Open', 'Pending Document Upload', 'Shortlisted',
			'Local Enquiry Approved', 'Selected', 'Local Enquiry Started',
			'Local Enquiry Rejected', 'Local Enquiry Completed', 'Accepted', 'Training Completed', 'Compensation Proposal Accepted', 'Compensation Proposal Created'
		];

		if (statuses.includes(frm.doc.status)) {
			frm.remove_custom_button(__('Local Enquiry Report'), __('Create'));
		}

		if (frm.doc.status === 'Accepted' || frm.doc.status === 'Training Completed') {
			// Remove "View" button and its inner options
			frm.remove_custom_button('View');
			frm.page.remove_inner_button('Job Offer', 'View');

			// Remove "Send Magic Link" button
			frm.remove_custom_button('Send Magic Link');

			// Remove "Rejected" and "Hold" options under "Set Status" button
			frm.page.remove_inner_button('Rejected', 'Set Status');
			frm.page.remove_inner_button('Hold', 'Set Status');
			frm.remove_custom_button(__('Job Offer'), __('Create'));
		}

		const magic_link_statuses = [
			'Interview Completed', 'Local Enquiry Approved', 'Selected',
			'Compensation Proposal Created', 'Compensation Proposal Accepted',
			'Interview Scheduled', 'Interview Ongoing'
		];

		if (magic_link_statuses.includes(frm.doc.status)) {
			frm.remove_custom_button('Send Magic Link');
		}

		if (frm.doc.status === 'Compensation Proposal Created' || frm.doc.status === 'Compensation Proposal Accepted') {
			frm.page.remove_inner_button('Rejected', 'Set Status');
			frm.page.remove_inner_button('Hold', 'Set Status');
		}

		if (frm.doc.status === 'Interview Scheduled' || frm.doc.status === 'Interview Ongoing') {
			frm.page.remove_inner_button('Local Enquiry Report', 'Create');
		}
	},
	job_title: function(frm) {
		if (frm.doc.job_title) {
			frappe.db.get_value('Job Opening', frm.doc.job_title, 'department', function (r) {
				if (r && r.department) {
					frm.set_value('department', r.department);
				}
			});
		}
	},
	status: function (frm) {
		frm.trigger('refresh');
	},
	date_of_birth: function(frm) {
		if (frm.doc.date_of_birth) {
			frappe.call({
				method: "beams.beams.custom_scripts.job_applicant.job_applicant.calculate_and_validate_age",
				args: {
					doc: frm.doc
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value("age", r.message);
					}
				}
			});
		}
	}
});

function handle_custom_buttons(frm) {
	if (!frm.is_new()) {
		if (frappe.user_roles.includes('HR Manager')) {
			// Handle "Appointment Letter" button for "Training Completed" status
			if (frm.doc.status === 'Training Completed') {
				frappe.db.get_value('Appointment Letter', { 'job_applicant': frm.doc.name }, 'name', function (result) {
					if (!result || !result.name) {
						frm.add_custom_button(__('Appointment Letter'), function () {
							frappe.new_doc('Appointment Letter', {
								job_applicant: frm.doc.name
							});
						}, __('Create'));
					}
				});
			}

			// Handle "Compensation Proposal" button for "Selected" status
			if (frm.doc.status === 'Selected') {
				frappe.db.get_value('Compensation Proposal', { 'job_applicant': frm.doc.name }, 'name', function (result) {
					if (!result || !result.name) {
						frm.add_custom_button(__('Compensation Proposal'), function () {
							frappe.new_doc('Compensation Proposal', {
								job_applicant: frm.doc.name
							});
						}, __('Create'));
					} else {
						frm.remove_custom_button(__('Compensation Proposal'), __('Create'));
					}
				});
			}

			// Show a "Local Enquiry Report (LER)" button in the Job Applicant form only when the status is "Shortlisted from Interview"
			if (frm.doc.status == 'Shortlisted from Interview') {
				frappe.call({
					method: 'beams.beams.custom_scripts.job_applicant.job_applicant.get_existing_local_enquiry_report',
					args: {
						doc_name: frm.doc.name
					},
					callback: function (response) {
						if (response.message) {
							frappe.db.get_doc('Local Enquiry Report', response.message).then(report => {
								frm.add_custom_button(__('Local Enquiry Report'), function () {
									frappe.set_route('Form', 'Local Enquiry Report', report.name);
								}, __('View'));
							});
						} else {
							frm.add_custom_button(__('Local Enquiry Report'), function () {
								frappe.call({
									method: 'beams.beams.custom_scripts.job_applicant.job_applicant.create_and_return_report',
									args: {
										job_applicant: frm.doc.name
									},
									callback: function (createResponse) {
										if (createResponse.message) {
											frm.add_custom_button(__('Local Enquiry Report'), function () {
												frappe.set_route('Form', 'Local Enquiry Report', createResponse.message);
											}, __('View'));
											frm.refresh();
										}
									}
								});
							}, __('Create'));
						}
					}
				});
			}

			if (frm.doc.status == 'Shortlisted' || frm.doc.status == 'Pending Document Upload') {
				frm.add_custom_button(__('Send Magic Link'), function () {
					frappe.confirm('Are you sure you want to send the magic link to the candidate?', function () {
						frappe.call({
							method: 'beams.beams.custom_scripts.job_applicant.job_applicant.send_magic_link',
							args: {
								applicant_id: frm.doc.name
							},
							callback: function (r) {
								if (r.message) {
									navigator.clipboard.writeText(r.message).then(function () {
										frappe.show_alert(__('Magic Link copied to clipboard!'));
									}).catch(function (err) {
										frappe.show_alert(__('Failed to copy Magic Link to clipboard'));
									});
								}
							}
						});
					});
				});
			}

			if (frm.doc.status === 'Accepted') {
				frm.add_custom_button(__('Training Completed'), function () {
					frm.set_value('status', 'Training Completed');
					frm.save();
				}, __('Set Status'));
			}

			if (frm.doc.status !== 'Rejected' && frm.doc.status !== 'Selected') {
				frm.add_custom_button(__('Rejected'), function () {
					frm.set_value('status', 'Rejected');
					frm.save();
				}, __('Set Status'));
			}

			// Show "Hold" button only if status is neither "Rejected" nor "Hold"
			if (frm.doc.status !== 'Hold' && frm.doc.status !== 'Rejected' && frm.doc.status !== 'Selected') {
				frm.add_custom_button(__('Hold'), function () {
					frm.set_value('status', 'Hold');
					frm.save();
				}, __('Set Status'));
			}

			if (['Hold', 'Local Enquiry Approved'].includes(frm.doc.status)) {
				frm.add_custom_button(__('Selected'), function () {
					frm.set_value('status', 'Selected');
					frm.save();
				}, __('Set Status'));
			}

			if (frm.doc.status === 'Open') {
				frm.add_custom_button(__('Shortlisted'), function () {
					frm.set_value('status', 'Shortlisted');
					frm.save();
				}, __('Set Status'));
			}

			if (frm.doc.status == 'Interview Completed') {
				frm.add_custom_button(__('Shortlisted from Interview'), function() {
					frm.set_value('status', 'Shortlisted from Interview');
					frm.save();
				}, __('Set Status'));
			}
		}
	}
}

frappe.ui.form.on('Applicant Interview Round', {
	create_interview: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Check if the form is dirty
		if (frm.is_dirty()) {
			frappe.msgprint(__('Please save your changes before creating or viewing an interview.'));
			return;
		}
		// View created Interviews. If no Interview exists, open a new unsaved Interview form with pre-filled values
		if (row.interview_reference) {
			frappe.set_route('Form', 'Interview', row.interview_reference);
		}
		else {
			if (!["Document Uploaded", "Interview Scheduled", "Interview Ongoing"].includes(frm.doc.status)){
				frappe.msgprint(__('Please upload the required documents before creating or viewing an interview.'));
				return;
			}
			frappe.model.with_doctype('Interview', function () {
				let new_interview = frappe.model.get_new_doc('Interview');
				new_interview.job_applicant = frm.doc.name;
				new_interview.job_title = frm.doc.job_opening;
				new_interview.interview_round = row.interview_round;
				new_interview.scheduled_on = frappe.datetime.now_date();
				new_interview.status = 'Pending';
				frappe.set_route('Form', 'Interview', new_interview.name);
			});
		}
	}
});