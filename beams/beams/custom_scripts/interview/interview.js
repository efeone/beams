frappe.ui.form.on('Interview', {
	refresh: function (frm) {
		if (frm.doc.average_final_score) {
				frm.set_value('average_final_score',
						parseFloat(frm.doc.average_final_score).toFixed(2)
				);
		}
		handle_hrms_custom_buttons(frm);

		let allowed_interviewers = [];
		frm.doc.interview_details.forEach(values => {
			allowed_interviewers.push(values.interviewer);
		});

		if (frm.doc.docstatus != 2 && !frm.doc.__islocal) {
			if (allowed_interviewers.includes(frappe.session.user)) {
				frappe.db.get_value(
					'Interview Feedback',
					{ 'interviewer': frappe.session.user, 'interview': frm.doc.name, 'docstatus': 1 },
					'name',
					(r) => {
						if (Object.keys(r).length === 0) {
							frm.add_custom_button(__('Submit Interview Feedback'), function () {
								frappe.call({
									method: 'beams.beams.custom_scripts.interview.interview.get_interview_skill_and_question_set',
									args: {
										interview_round: frm.doc.interview_round,
										interviewer: frappe.session.user,
										interview_name: frm.doc.name,
									},
									callback: function (r) {
										if (r.message) {
											frm.events.show_custom_feedback_dialog(frm, r.message[1], r.message[0], r.message[2]);
										}
										frm.refresh();
									},
									freeze: true,
									freeze_message: __("Fetching interview details..!")
								});
							}).addClass('btn-primary');
						}
					}
				);
			}
		}

		if (frm.doc.job_applicant && !frm.is_new()) {
			frm.add_custom_button(__('Job Applicant'), function () {
				frappe.set_route('Form', 'Job Applicant', frm.doc.job_applicant);
			}, 'View');

			frm.add_custom_button(__('Resume'), function () {
				frappe.db.get_value('Job Applicant', frm.doc.job_applicant, 'resume_attachment')
					.then(r => {
						let site_url = frappe.urllib.get_base_url();
						let resume_path = r.message.resume_attachment;
						if (!resume_path) {
							frappe.msgprint("No Attached Resume");
						} else {
							let file_url = `${site_url}${resume_path}`;
							window.open(file_url, '_blank');
						}
					});
			}, 'View');
		}
	},
	job_applicant(frm) {
		set_job_applicant_dashboard(frm);
	},
	validate: function(frm) {
		if (frm.doc.from_time && frm.doc.to_time && frm.doc.scheduled_on) {

			let scheduled_on = frm.doc.scheduled_on;

			// Convert time strings into Date objects for proper comparison
			let from_time = new Date(`${scheduled_on}T${frm.doc.from_time}`);
			let to_time = new Date(`${scheduled_on}T${frm.doc.to_time}`);

			let today = frappe.datetime.get_today();

			if (frm.doc.scheduled_on && frm.doc.scheduled_on < today) {
				frappe.throw(__("Interview date cannot be in the past."));
			}
			if (to_time <= from_time) {
				frappe.throw(__("End Time (To Time) must be greater than Start Time (From Time)."));
			}
		}
	},

	show_custom_feedback_dialog: function (frm, data, question_data, feedback_exists) {
		let fields = frm.events.get_fields_for_custom_feedback();
		fields.push({ fieldtype: 'Data', fieldname: 'parent', hidden: 1, label: __('Parent') });
		fields.push({ fieldtype: 'Data', fieldname: 'name', hidden: 1, label: __('Name') });

		let dialog_fields = [
			{
				fieldname: 'skill_set',
				fieldtype: 'Table',
				label: __('Skill Assessment'),
				cannot_add_rows: true,
				in_editable_grid: true,
				reqd: 1,
				fields: fields,
				data: data
			}
		];

		if (question_data && question_data.length > 0) {
			let question_fields = frm.events.get_fields_for_questions();
			dialog_fields.push({
				fieldname: 'questions',
				fieldtype: 'Table',
				label: __('Question Assessment'),
				cannot_add_rows: true,
				in_editable_grid: true,
				reqd: 1,
				fields: question_fields,
				data: question_data
			});
		}

		dialog_fields.push(
			{
				fieldname: 'result',
				fieldtype: 'Select',
				label: __('Result'),
				options: ['', 'Cleared', 'Rejected'],
				default: '',
				reqd: 1
			},
			{
				fieldname: 'feedback',
				fieldtype: 'Small Text',
				label: __('Feedback')
			}
		);

		let d = new frappe.ui.Dialog({
			title: __('Submit Feedback'),
			fields: dialog_fields,
			size: 'large',
			minimizable: true,
			primary_action_label: __("Save"),
			primary_action: function (values) {
				if (!validate_feedback_dialog(d)) return;
				create_interview_feedback(frm, values, feedback_exists, 'save');
				d.hide();
			},
			secondary_action_label: __("Save and Submit"),
			secondary_action: function () {
				let values = d.get_values();
				if (!validate_feedback_dialog(d)) return;
				create_interview_feedback(frm, d.get_values(), feedback_exists, 'submit');
				d.hide();
			}
		});

		d.show();
		d.set_value('result', '');

		frappe.db.get_value('Interview Feedback', { "job_applicant": frm.doc.job_applicant,"interview": frm.doc.name,"interviewer": frappe.session.user}, ['result', 'feedback'])
			.then(r => {
				if (r && r.message) {
					d.set_values({
						result: r.message.result || '',
						feedback: r.message.feedback || ''
					});
				}
			})
			.catch(err => {
				console.error("Error fetching interview feedback:", err);
			});

		frappe.after_ajax(() => {
			let skill_grid = d.fields_dict.skill_set.grid;
			skill_grid.wrapper.on('change', 'input[data-fieldname="score"]', function () {
				let row = skill_grid.get_selected();
				if (!row) return;

				let value = parseFloat($(this).val()) || 0;
				if (value > 10) {
					frappe.msgprint(__('Score cannot be greater than 10'));
				} else if (value < 0) {
					frappe.msgprint(__('Score cannot be less than 0'));
				}
				skill_grid.refresh();
			});

			if (d.fields_dict.questions) {
				let question_grid = d.fields_dict.questions.grid;
				question_grid.wrapper.on('change', 'input[data-fieldname="score"]', function () {
					let row = question_grid.get_selected();
					if (!row) return;

					let value = parseFloat($(this).val()) || 0;
					if (value > 10) {
						frappe.msgprint(__('Score cannot be greater than 10'));
					} else if (value < 0) {
						frappe.msgprint(__('Score cannot be less than 0'));
					}
					question_grid.refresh();
				});
			}
		});
	},

	get_fields_for_questions: function () {
		return [
			{ fieldtype: 'Data', fieldname: 'question', in_list_view: 1, label: __('Question') },
			{ fieldtype: 'Data', fieldname: 'answer', label: __('Answer') },
			{ fieldtype: 'Float', fieldname: 'weight', label: __('Weight') },
			{ fieldtype: 'Data', fieldname: 'applicant_answer', label: __('Applicant Answer'), in_list_view: 1 },
			{ fieldtype: 'Float', fieldname: 'score', label: __('Score (Out of 10)'), in_list_view: 1, reqd: 1 },
			{ fieldtype: 'Data', fieldname: 'parent', hidden: 1, label: __('Parent') },
			{ fieldtype: 'Data', fieldname: 'name', hidden: 1, label: __('Name') }
		];
	},

	get_fields_for_custom_feedback: function () {
		return [
			{ fieldtype: 'Link', fieldname: 'skill', label: __('Skill'), options: 'Skill', in_list_view: 1, reqd: 1 },
			{ fieldtype: 'Float', fieldname: 'score', label: __('Score (Out of 10)'), in_list_view: 1, reqd: 1 },
			{ fieldtype: 'Small Text', fieldname: 'remarks', label: __('Remarks') }
		];
	}
});

// Validates the interview feedback dialog before submission.
function validate_feedback_dialog(dialog) {
	const missing_fields = [];
	const skill_data = dialog.get_value('skill_set') || [];
	const question_data = dialog.fields_dict.questions ? (dialog.get_value('questions') || []) : [];

	// Check if Skill Assessment has data
	if (!skill_data.length) {
		missing_fields.push(__('Skill Assessment'));
	}

	for (let skill of skill_data) {
		if (!skill.skill || skill.score == null) {
			missing_fields.push(__('Skill (in Skill Assessment)'));
			break;
		}
		if (skill.score < 0 || skill.score > 10) {
			frappe.msgprint(__('Skill Score must be between 0 and 10.'));
			return false;
		}
	}

	// Check Question Assessment
	if (dialog.fields_dict.questions) {
		if (!question_data.length) {
			missing_fields.push(__('Question Assessment'));
		}

		for (let q of question_data) {
	     if (q.score == null) {
	             missing_fields.push(__('Score (in Question Assessment)'));
	             break;
	     }

			if (q.score < 0 || q.score > 10) {
				frappe.msgprint(__('Question Score must be between 0 and 10.'));
				return false;
			}
		}
	}
   // Check result explicitly
   if (!dialog.get_value('result')) {
           return false;
   }

	// Show unified missing fields error
	if (missing_fields.length > 0) {
		frappe.throw({
			title: __('Missing Values Required'),
			message: __('Following fields have missing values:') + '<br><ul>' + missing_fields.map(f => `<li>${f}</li>`).join('') + '</ul>'
		});
		return false;
	}

	return true;
}

var remove_custom_button_from_mobile_view = function (frm, label) {
	// Find the span element with the specified data-label attribute
	var span_element = $(`.menu-item-label[data-label='${encodeURIComponent(label)}']`);
	// Get the parent li element
	var parent_li_element = span_element.closest("li");
	// Hide the parent li element
	parent_li_element.hide();
}

var create_interview_feedback = function (frm, values, feedback_exists, save_submit) {
	var args = {
		data: values,
		interview_name: frm.doc.name,
		interviewer: frappe.session.user,
		job_applicant: frm.doc.job_applicant,
		method: save_submit
	};
	if (feedback_exists) {
		args['feedback_exists'] = feedback_exists;
	}
	frappe.call({
		method: 'beams.beams.custom_scripts.interview.interview.create_interview_feedback',
		args: args
	}).then(() => {
		frm.refresh();
	});
}

function handle_hrms_custom_buttons(frm) {
	setTimeout(function () {
		frm.remove_custom_button('Submit Feedback');
		remove_custom_button_from_mobile_view(frm, "Submit Feedback");
	}, 100);

	// Manage primary action buttons
	setTimeout(function () {
		if (!frm.is_dirty() && frm.doc.docstatus == 0) {
			frm.page.clear_primary_action();
			frm.page.set_primary_action(__('Submit'), function () {
				frm.savesubmit();
			});
		} else if (frm.is_dirty() && frm.doc.docstatus == 0) {
			frm.page.clear_primary_action();
			frm.page.set_primary_action(__('Save'), function () {
				frm.save();
			});
		} else if (frm.doc.docstatus == 1) {
			frm.page.clear_primary_action();
		}
	}, 100);
}

/**
 * Fetches and renders the Job Applicant dashboard in the Interview form.
 *
 * Calls the server-side method to get an HTML snippet showing basic applicant details
 * and injects it into the 'interview_html_field' section of the form.
 *
 */
function set_job_applicant_dashboard(frm) {
	if (!frm.doc.job_applicant) return;
		frappe.call({
			method: 'beams.beams.custom_scripts.interview.interview.get_job_applicant_dashboard_html',
			args: {
				job_applicant: frm.doc.job_applicant,
			},
			callback: function (r) {
				if (r.message && r.message.html) {
					$(frm.fields_dict['interview_html_field'].wrapper).html(r.message.html);
					frm.refresh_field('interview_html_field');
				}
			}
		});
}
