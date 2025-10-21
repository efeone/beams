frappe.ui.form.on('Appraisal', {
	refresh: function (frm) {
		frm.toggle_reqd('appraisal_cycle', 0);
		if (!frm.doc) return;
		salary_amount_read_only(frm);
		frm.trigger('update_self_kra_rating_list_view');
		frm.remove_custom_button(__('View Goals'));
		set_table_properties(frm, 'employee_self_kra_rating');
		set_table_properties(frm, 'dept_self_kra_rating');
		set_table_properties(frm, 'company_self_kra_rating');
		set_marks_read_only(frm, 'dept_self_kra_rating','marks');
		set_marks_read_only(frm, 'company_self_kra_rating','marks');
		set_marks_read_only(frm, 'employee_self_kra_rating','marks');
		set_marks_read_only(frm,'appraisal_kra','kra_goals');
		// Remove the button by targeting its full class list
		setTimeout(() => {
			$('.new-feedback-btn.btn.btn-sm.d-inline-flex.align-items-center.justify-content-center.px-3.py-2.border').remove();
		}, 500);
		// Hide dashboard
		$('.form-dashboard-section').hide();
		setTimeout(() => {
			$('.new-feedback-btn.btn.btn-sm.d-inline-flex.align-items-center.justify-content-center.px-3.py-2.border').remove();
		}, 500);

		frm.set_df_property('final_score', 'hidden', 1);

		// Show "New Feedback" button only if the user is an assessment officer and not the appraised employee, before submission

		if (!frm.is_new() && frm.doc.docstatus !== 1) {
			let user = frappe.session.user;

			frappe.call({
				method: "beams.beams.custom_scripts.appraisal.appraisal.get_primary_assessment_officer",
				args: { employee_id: frm.doc.employee },
				callback: function(r) {
					let primary_officer_user = r.message;

					if (primary_officer_user === user) {
						frappe.call({
							method: 'beams.beams.custom_scripts.appraisal.appraisal.get_feedback_for_appraisal',
							args: { appraisal_name: frm.doc.name },
							callback: function (r) {
								const feedback_name = r.message;
								if (!feedback_name) {
									frm.add_custom_button(__('New Feedback'), () => {
										frm.events.show_feedback_dialog(frm);
									});
								} else {
									frappe.db.get_value('Employee Performance Feedback', feedback_name, 'docstatus')
										.then(val => {
											const docstatus = val.message?.docstatus;
											if (docstatus === 0) {
												frm.add_custom_button(__('Edit Feedback'), () => {
													frm.events.show_feedback_dialog(frm);
												});
											}
										});
								}
							}
						});
					}
				}
			});
		}

		if (!frm.is_new() && frm.doc.category_details.length <= 0) {
			frappe.db.get_value("Employee", frm.doc.employee, "user_id", (r) => {
				if (r && r.user_id === frappe.session.user) {

					frm.add_custom_button(__('Notify Assessment Officers'), function () {
						if (frm.doc.__unsaved) {
							frappe.msgprint(__('Please save the form before sending notification.'));
							return;
						}

						frappe.confirm(
							'Do you want to send the notification to your Assessment Officer?',
							() => {
								frappe.call({
									method: "beams.beams.custom_scripts.appraisal.appraisal.notify_assestment_officer",
									args: {
										doc: frm.doc.name,
										employee_id: frm.doc.employee
									},
									callback: (response) => {
										if (!response.exc) {
											frappe.msgprint('Notification sent and tasks assigned.');
										}
									}
								});
							}
						);
					}).addClass("btn-primary");

				}
			});
		}

		if (frm.doc.name) {
			// Check if appraisal_template is set before calling get_appraisal_summary
			if (frm.doc.appraisal_template) {
				// Fetch the Employee Performance Feedback related to the Appraisal
				frappe.call({
					method: "beams.beams.custom_scripts.appraisal.appraisal.get_feedback_for_appraisal",
					args: {
						appraisal_name: frm.doc.name
					},
					callback: function (res) {
						if (res.message) {
							const employee_feedback = res.message;

							frappe.call({
								method: "beams.beams.custom_scripts.appraisal.appraisal.get_appraisal_summary",
								args: {
									appraisal_template: frm.doc.appraisal_template,
									employee_feedback: employee_feedback
								},
								callback: function (r) {
									if (r.message) {
										$(frm.fields_dict['appraisal_summary'].wrapper).html(r.message[0]);
										if (frm.doc.final_average_score != r.message[1]) {
											frm.set_value("final_average_score", r.message[1])
											frm.refresh_field("final_average_score")
										}
									}
								}
							});
						} else {
							$(frm.fields_dict['appraisal_summary'].wrapper).html('<p>No Employee Performance Feedback found for this appraisal.</p>');
						}
					}
				});
			} else {
				$(frm.fields_dict['appraisal_summary'].wrapper).html('<p>No Employee Performance Feedback is found.</p>');
			}
		} else {
			$(frm.fields_dict['appraisal_summary'].wrapper).html('<p>Please save the Appraisal to view the summary.</p>');
		}

		if (frm.doc.employee) {
			frappe.call({
				method: "beams.beams.custom_scripts.appraisal.appraisal.check_existing_event",
				args: { appraisal_reference: frm.doc.name },
				callback: function (r) {
					if (r.message) {
						// Remove existing "View Event" button before adding a new one
						frm.fields_dict["view_event_button"]?.$wrapper.find('button').remove();

						// Add "View Event" as a separate button
						frm.add_custom_button(__('View Event'), function () {
							frappe.set_route('Form', 'Event', r.message);
						});
					}
				}
			});
			// Add "One to One Meeting" inside the "Create" dropdown
			const allowed_roles = ['HR Manager', 'HOD'];
			const user_has_access = frappe.user_roles.some(role => allowed_roles.includes(role));
			if (user_has_access) {
				frm.add_custom_button(__('One to One Meeting'), function () {
					frappe.model.open_mapped_doc({
						method: "beams.beams.custom_scripts.appraisal.appraisal.map_appraisal_to_event",
						args: { source_name: frm.doc.name },
						frm: frm
					});
				}, __('Create'));
			}
		}

		frappe.call({
			method: "beams.beams.custom_scripts.appraisal.appraisal.get_categories_table",
			callback: function (res) {
				if (res.message) {
					frm.set_df_property('category_html', 'options', res.message);
				} else {
					frm.set_df_property('category_html', 'options', '<p>No categories found.</p>');
				}
			}
		});

		frappe.db.get_value("Employee",{user_id:frappe.session.user},["name"]).then(res => {
		// Dynamically add the "Add Category" button only once
			const current_emp_id = res.message?.name;
			if (current_emp_id && current_emp_id !== frm.doc.employee){
				if (!frm.category_button_added) {
					const button_html = `
						<button class="btn btn-primary" id="add_category_button" style="margin-top: 10px;">Add Category</button><br><br>
					`;
					$(frm.fields_dict['category_html'].wrapper).after(button_html);
					frm.category_button_added = true;

					// Button click event for adding a category
					$('#add_category_button').on('click', function () {
						frm.events.show_add_category_dialog(frm);
					});
				}
			}
		})
		// Hide the chart by targeting its container
		if (frm.dashboard.wrapper) {
			frm.dashboard.wrapper.find('.chart-container').hide(); // Adjust selector as needed
		}

		['employee_self_kra_rating', 'dept_self_kra_rating', 'company_self_kra_rating'].forEach(field => {
			frm.fields_dict[field].grid.wrapper.on('change', 'input[data-fieldname="marks"]', function () {
				let value = parseFloat($(this).val());
				if (value > 5) {
					frappe.msgprint(__('Marks cannot be greater than 5.'));
					$(this).val('');  // Reset invalid value
				}
			});
		});
		const current_user = frappe.session.user;
		frappe.db.get_value("Employee", { user_id: current_user }, ["name"]).then(emp_res => {
			const emp = emp_res.message?.name;

			if (emp && emp === frm.doc.employee && frm.doc.end_date) {
				const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
				const end_date = frappe.datetime.str_to_obj(frm.doc.end_date);
				if (today > end_date) {
					frm.disable_form();
					frappe.show_alert({
						message: __("This appraisal is read-only since the appraisal period has ended."),
						indicator: "red"
					});
				}
			}
		});
		frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name")
			.then(r => {
				const emp = r.message?.name;
				if (emp && emp === frm.doc.employee && frm.doc.salary_increment_amount <= 0) {
					hide_employee_fields(frm);
					show_final_assessment_progress(frm, emp);
				}
			});
		if (!frm.is_new()) {
			const today = frappe.datetime.get_today();
			const start_date = frm.doc.start_date;
			const appraisal_period_started = start_date && today >= start_date;
			if (!frm.doc.consent_received) {
				frm.disable_form();
				frm.dashboard.set_headline_alert(
					__("Waiting for Employee Appraisal Consent Submission"), "orange"
				);
			} else if (!appraisal_period_started) {
				frm.disable_form();
				frm.dashboard.set_headline_alert(
				__("Appraisal period will begin on {0}. Form will be editable after this date.",
					[frappe.datetime.str_to_user(start_date)]
				),
				"green"
			);
			}
			else {
				frm.enable_form();
			}
		}
		if (frm.doc.employee) {
			frappe.db.get_value("Employee", frm.doc.employee, "employment_type")
				.then(r => {
					if (r && r.message && r.message.employment_type === "Contract") {
						// Set indicator on page header
						frm.page.set_indicator(__('Contract Employee'), 'red');
					}
				});
		}
	},
	employee: function (frm) {
		if (frm.doc.employee) {
			frappe.db.get_value("Employee", frm.doc.employee, "salary_structure", (r) => {
				if (r && r.salary_structure) {
					frm.set_value("salary_structure", r.salary_structure);
				}
				else {
					frm.set_value("salary_structure", '')
				}
			});
		}
	},
	validate: function (frm) {
		for (let field of ['employee_self_kra_rating', 'dept_self_kra_rating', 'company_self_kra_rating']) {
			if (frm.doc[field] && frm.doc[field].some(row => row.marks > 5)) {
				frappe.throw(__('Marks cannot be greater than 5.'));
			}
		}
	},

   show_feedback_dialog: function (frm) {
	let dialog = new frappe.ui.Dialog({
		title: 'New Feedback',
		fields: [
			{
				label: 'Employee Criteria',
				fieldname: 'employee_criteria',
				fieldtype: 'Table',
				fields: [
					{
						label: 'Criteria',
						fieldname: 'criteria',
						fieldtype: 'Link',
						options: 'Employee Feedback Criteria',
						in_list_view: 1,
						reqd: 1,
						read_only: 1,
						columns: 3
					},
					{
						label: 'Goals',
						fieldname: 'goals',
						fieldtype: 'Text Editor',
						in_list_view: 1,
						read_only: 1,
						columns: 3
					},
					{
						label: 'Weightage(%)',
						fieldname: 'per_weightage',
						fieldtype: 'Percent',
						in_list_view: 1,
						columns: 2,
						read_only: 1,
						reqd: 1
					},
					{
						label: 'Marks (out of 5)',
						fieldname: 'marks',
						fieldtype: 'Float',
						in_list_view: 1,
						reqd: 1,
						columns: 2,
						description: 'Enter Marks (0 - 5)'
					},
				],
				cannot_add_rows: true,
			},
			{
				label: 'Department Criteria',
				fieldname: 'department_criteria',
				fieldtype: 'Table',
				fields: [
					{
						label: 'Criteria',
						fieldname: 'criteria',
						fieldtype: 'Link',
						options: 'Employee Feedback Criteria',
						in_list_view: 1,
						read_only: 1,
						reqd: 1,
					},
					{
						label: 'Weightage(%)',
						fieldname: 'per_weightage',
						fieldtype: 'Percent',
						in_list_view: 1,
						read_only: 1,
						reqd: 1,
					},
					{
						label: 'Marks (out of 5)',
						fieldname: 'marks',
						fieldtype: 'Float',
						in_list_view: 1,
						reqd: 1,
						description: 'Enter Marks (0 - 5)',
					},
				],
				cannot_add_rows: true,
			},
			{
				label: 'Company Criteria',
				fieldname: 'company_criteria',
				fieldtype: 'Table',
				fields: [
					{
						label: 'Criteria',
						fieldname: 'criteria',
						fieldtype: 'Link',
						options: 'Employee Feedback Criteria',
						in_list_view: 1,
						read_only: 1,
						reqd: 1,
					},
					{
						label: 'Weightage(%)',
						fieldname: 'per_weightage',
						fieldtype: 'Percent',
						in_list_view: 1,
						read_only: 1,
						reqd: 1,
					},
					{
						label: 'Marks (out of 5)',
						fieldname: 'marks',
						fieldtype: 'Float',
						in_list_view: 1,
						reqd: 1,
						description: 'Enter Marks (0 - 5)',
					},
				],
				cannot_add_rows: true,
			},
			{
				label: 'Feedback',
				fieldname: 'feedback',
				fieldtype: 'Text Editor',
				enable_mentions: true,
			},
		],
		size: 'extra-large',
		primary_action_label: 'Submit',
		primary_action(values) {
			const validate_marks = (table) => {
				let is_valid = true;
				table.forEach(row => {
					if (row.marks === '' || row.marks == null) {
						frappe.msgprint(__('Marks cannot be empty.'));
						is_valid = false;
					} else if (row.marks < 0 || row.marks > 5) {
						frappe.msgprint(__('Marks must be between 0 and 5.'));
						is_valid = false;
					}
				});
				return is_valid;
			};
			const feedback_is_empty = !values.feedback || values.feedback.replace(/<[^>]*>/g, '').trim() === '';
			if (feedback_is_empty) {
				frappe.msgprint(__('Please enter feedback before submitting.'));
				return;
			}

			if (
				validate_marks(values.employee_criteria) &&
				validate_marks(values.department_criteria) &&
				validate_marks(values.company_criteria)
			) {
				frappe.call({
					method: "beams.beams.custom_scripts.appraisal.appraisal.create_employee_feedback",
					args: {
						data: values,
						appraisal_name: frm.doc.name,
						employee: frm.doc.employee,
						method: 'submit',
						feedback_exists: dialog.feedback_exists || null
					},
					callback: function () {
						frappe.msgprint(__('Feedback has been submitted successfully.'));
						frm.reload_doc();
						dialog.hide();
					}
				});
			}
		},
		secondary_action_label: 'Save',
		secondary_action() {
		const values = dialog.get_values();
		if (!values) return;


		frappe.call({
			method: "beams.beams.custom_scripts.appraisal.appraisal.create_employee_feedback",
			args: {
				data: JSON.stringify(values),
				appraisal_name: frm.doc.name,
				employee: frm.doc.employee,
				method: 'save',
				feedback_exists: dialog.feedback_exists || null
			},
			callback: function () {
				frappe.msgprint(__('Feedback has been saved successfully.'));
				frm.reload_doc();  
				dialog.hide();
			}
		});
	}

	});

	dialog.fields_dict.employee_criteria.df.data = frm.doc.appraisal_kra.map(row => ({
		criteria: row.kra,
		goals: row.kra_goals,
		per_weightage: row.per_weightage,
	}));
	dialog.fields_dict.employee_criteria.refresh();

	if (frm.doc.appraisal_template) {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Appraisal Template",
				name: frm.doc.appraisal_template
			},
			callback: function (res) {
				if (res.message) {
					dialog.fields_dict.department_criteria.df.data = res.message.department_rating_criteria.map(row => ({
						criteria: row.criteria,
						per_weightage: row.per_weightage
					}));
					dialog.fields_dict.company_criteria.df.data = res.message.company_rating_criteria.map(row => ({
						criteria: row.criteria,
						per_weightage: row.per_weightage
					}));
					dialog.fields_dict.department_criteria.refresh();
					dialog.fields_dict.company_criteria.refresh();
				}
			}
		});
	}

	frappe.call({
		method: "beams.beams.custom_scripts.appraisal.appraisal.get_existing_feedback_data",
		args: { appraisal_name: frm.doc.name },
		callback: function (r) {
			if (r.message) {
				const feedback = r.message;
				dialog.feedback_exists = feedback.name;

				const set_marks = (source_list, fieldname) => {
					const table = dialog.fields_dict[fieldname].df.data;
					source_list.forEach(src => {
						const row = table.find(r => r.criteria === src.criteria);
						if (row) row.marks = src.marks;
					});
					dialog.fields_dict[fieldname].refresh();
				};

				if (feedback.employee_criteria && feedback.employee_criteria.length) {
					dialog.fields_dict.employee_criteria.df.data = feedback.employee_criteria;
				}
				dialog.fields_dict.employee_criteria.refresh();
				set_marks(feedback.employee_criteria || [], "employee_criteria");
				set_marks(feedback.department_criteria || [], "department_criteria");
				set_marks(feedback.company_criteria || [], "company_criteria");

				dialog.set_value("feedback", feedback.feedback || '');
			}
		}
	});
	dialog.show();
},


	open_add_category_dialog: function (frm) {
		const dialog = new frappe.ui.Dialog({
			title: 'Add Category',
			fields: [
				{ label: 'Select Category', fieldname: 'select_category', fieldtype: 'Link', options: 'Appraisal Category', only_select: 1, reqd: 1 },
				{ label: 'Remarks', fieldname: 'remarks', fieldtype: 'Text', reqd: 1 },
			],
			primary_action_label: 'Submit',
			primary_action(data) {
				if (data.select_category && data.remarks) {
					frappe.call({
						method: "beams.beams.custom_scripts.appraisal.appraisal.add_to_category_details",
						args: {
							parent_docname: frm.doc.name,
							category: data.select_category,
							remarks: data.remarks
						},
						callback(res) {
							if (res.message === "Success") {
								frappe.msgprint(__('Category successfully added to Category Details.'));
								frappe.call({
									method: "beams.beams.custom_scripts.appraisal.appraisal.send_next_officer_notification",
									args: { appraisal_name: frm.doc.name },
									callback(response) {
										if (response.message && response.message.includes("Notification logged for")) {
											const notified_officer = response.message.split("Notification logged for ")[1];
											frappe.msgprint(__('Notification sent to Assessment Officer: {0}', [notified_officer]));
										}
									}
								});
								frm.reload_doc();
								dialog.hide();
							} else {
								frappe.msgprint(__('Failed to add category.'));
							}
						}
					});
				} else {
					frappe.msgprint(__('Please fill all mandatory fields.'));
				}
			}
		});

		dialog.show();
	},
	show_add_category_dialog: function (frm) {
		/**
		* Shows the "Add Category" dialog if the user is permitted and feedback exists.
		* For assessmnet officer
		*/
		const current_user = frappe.session.user;

		frappe.db.get_value("Employee", { user_id: current_user }, ["name"]).then(emp_res => {
			const current_emp_id = emp_res.message?.name;
			frappe.call({
				method: "beams.beams.custom_scripts.appraisal.appraisal.get_primary_assessment_officer",
				args: { employee_id: frm.doc.employee },
				callback: function(r) {
					const assigned_officer = r.message;

					if (current_user === assigned_officer) {
						// Only primary officer must add feedback before adding category
						frappe.call({
							method: "beams.beams.custom_scripts.appraisal.appraisal.check_feedback_exists",
							args: {
								appraisal_name: frm.doc.name,
								assessment_officer_user_id: current_user,
								employee: frm.doc.employee
							},
							callback: function(res) {
								if (res.message) {
									frm.events.open_add_category_dialog(frm);
								} else {
									frappe.msgprint(__('You must add performance feedback before adding a category.'));
								}
							}
						});
					} else {
						frm.events.open_add_category_dialog(frm);
					}
				}
			});
		});

	},


	//Updates or clears child tables based on the selected appraisal template by fetching and populating criteria data
	appraisal_template: function (frm) {
		if (frm.doc.appraisal_template) {
			frappe.call({
				method: "beams.beams.custom_scripts.appraisal.appraisal.get_appraisal_template_criteria",
				args: {
					appraisal_template_name: frm.doc.appraisal_template
				},
				callback: function (response) {
					if (response.message.success) {
						const { employee_criteria, department_criteria, company_criteria } = response.message;
						// Clear existing rows in all child tables
						frm.clear_table("employee_self_kra_rating");
						frm.clear_table("dept_self_kra_rating");
						frm.clear_table("company_self_kra_rating");
						// Populate Employee criteria
						employee_criteria.forEach(item => {
							const new_row = frm.add_child("employee_self_kra_rating");
							new_row.criteria = item.criteria;
							new_row.per_weightage = item.per_weightage;
						});
						// Populate Department criteria
						department_criteria.forEach(item => {
							const new_row = frm.add_child("dept_self_kra_rating");
							new_row.criteria = item.criteria;
							new_row.per_weightage = item.per_weightage;
						});
						// Populate Company criteria
						company_criteria.forEach(item => {
							const new_row = frm.add_child("company_self_kra_rating");
							new_row.criteria = item.criteria;
							new_row.per_weightage = item.per_weightage;
						});
						frm.refresh_field("employee_self_kra_rating");
						frm.refresh_field("dept_self_kra_rating");
						frm.refresh_field("company_self_kra_rating");
					}
				}
			});
		} else {
			// Clear all child tables if no template is selected
			frm.clear_table("employee_self_kra_rating");
			frm.clear_table("dept_self_kra_rating");
			frm.clear_table("company_self_kra_rating");
			frm.refresh_field("employee_self_kra_rating");
			frm.refresh_field("dept_self_kra_rating");
			frm.refresh_field("company_self_kra_rating");
		}
	},
	update_self_kra_rating_list_view: function (frm) {
		/**
		* Dynamically updates the "rating" and "marks" fields to be visible in the list view
		* for multiple child tables in the Appraisal doctype.
		*/
		let child_tables = ["employee_self_kra_rating", "dept_self_kra_rating", "company_self_kra_rating"];
		child_tables.forEach(child_table => {
			if (frm.fields_dict[child_table]) {
				frm.fields_dict[child_table].grid.update_docfield_property("rating", "in_list_view", 1);
				frm.fields_dict[child_table].grid.update_docfield_property("marks", "in_list_view", 1);
				frm.fields_dict[child_table].grid.reset_grid();
				frm.refresh_field(child_table);
			}
		});
	},
	salary_increment_amount: function(frm) {
		if (frm.doc.employee_ctc && frm.doc.salary_increment_amount) {
			let percentage = (frm.doc.salary_increment_amount / frm.doc.employee_ctc) * 100;
			frm.set_value("salary_increment_percentage", percentage.toFixed(2));
		}
	}
});

function set_table_properties(frm, table_name) {
	const fields = ['criteria', 'per_weightage', 'rating'];
	fields.forEach(field => {
		frm.fields_dict[table_name].grid.update_docfield_property(field, 'read_only', 1);
	});
	frm.set_df_property(table_name, 'cannot_add_rows', true);
	frm.set_df_property(table_name, 'cannot_delete_rows', true);
	frm.set_df_property(table_name, 'cannot_delete_all_rows', true);
}

frappe.ui.form.on('Employee Feedback Rating', {
	marks: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.marks > 5) {
			frappe.msgprint(__('Marks cannot be greater than 5.'));
			frappe.model.set_value(cdt, cdn, 'marks', 0);
		} else if (row.marks < 0) {
			frappe.msgprint(__('Marks cannot be less than 0.'));
			frappe.model.set_value(cdt, cdn, 'marks', 0);
		}
		else {
			row.rating = row.marks / 5
		}
		frm.refresh_fields();
	}
});

/**
* Sets the "marks" field in a given child table to read-only or editable
* depending on whether the logged-in user is the Administrator or the employee
*/
function set_marks_read_only(frm, table_name,field_name) {
	frappe.db.get_value("Employee", { user_id: frappe.session.user }, ["name"]).then(res => {
		const emp_id = res.message?.name || null;
		const is_admin = frappe.session.user === "Administrator";
		if (!is_admin && emp_id !== frm.doc.employee ){
			frm.fields_dict[table_name].grid.update_docfield_property(field_name, 'read_only', 1);
		} else {
			frm.fields_dict[table_name].grid.update_docfield_property(field_name, 'read_only', 0);
		}
	});
}

/**
* Sets the "salary_increment_amount" field as read-only
* if the logged-in user does not have the "Salary Increment Approver" role.
*/
function salary_amount_read_only(frm) {
	if (!frappe.user_roles.includes("Salary Increment Approver")) {
		frm.set_df_property("salary_increment_amount", "read_only", 1);
		frm.set_df_property("salary_structure", "read_only", 1);
		frm.set_df_property("salary_assignment_from_date", "read_only", 1);
		frm.set_df_property("create_salary_assignment", "read_only", 1);
		frm.set_df_property("allow_double_increment", "read_only", 1)
	} else {
		frm.set_df_property("salary_increment_amount", "read_only", 0);
		frm.set_df_property("salary_structure", "read_only", 0);
		frm.set_df_property("salary_assignment_from_date", "read_only", 0);
		frm.set_df_property("create_salary_assignment", "read_only", 0);
		frm.set_df_property("allow_double_increment", "read_only", 0)
	}
}
/**
 * Hides a set of fields from the Appraisal form for the logged-in employee.
 */
function hide_employee_fields(frm) {
	const fields_to_hide = [
		"final_performance_category",
		"salary_increment_percentage",
		"salary_increment_amount",
		"category_based_on_marks",
		"employee_ctc",
		"appraisal_summary",
		"feedback_html",
		"final_average_score"
	];

	fields_to_hide.forEach(fieldname => {
		frm.set_df_property(fieldname, "hidden", 1);
	});
}
/**
 * Fetches the assessment officers for the employee and displays a progress bar
 * showing how many officers have submitted their final assessment categories.
 */
function show_final_assessment_progress(frm, emp) {
	frappe.db.get_doc("Employee", emp).then(employee_doc => {
		const officer_users = (employee_doc.assessment_officers || []).map(row => row.assessment_officer);
		const total_officers = officer_users.length;

		if (total_officers === 0) return;

		frappe.db.get_list("Employee", {
			filters: { user_id: ["in", officer_users] },
			fields: ["name", "user_id"]
		}).then(officer_employees => {
			const officer_employee_ids = officer_employees.map(e => e.name);
			const category_details = frm.doc.category_details || [];
			const completed_count = category_details.length;
			const progress = Math.round((completed_count / total_officers) * 100);

			if (frm.fields_dict.category_details && frm.fields_dict.category_details.wrapper) {
				const wrapper = $(frm.fields_dict.category_details.wrapper);
				wrapper.html(get_progress_html(progress, completed_count, total_officers));
			}
		});
	});
}
/**
 * Generates an HTML snippet for the Final Assessment Progress bar.
 */
function get_progress_html(progress, completed, total) {
	const color = (progress === 100) ? "#4caf50" :
				  (progress > 50) ? "#00bcd4" :
				  "#ff6b6b";

	return `
		<div style="padding:20px;text-align:center;">
			<h4>Final Assessment Progress</h4>
			<p>${completed} of ${total} assessment officers have added their categories.</p>
			<div style="background:#eee;border-radius:6px;height:16px;overflow:hidden;margin-top:10px;">
				<div style="width:${progress}%;background:${color};height:100%;transition:width .4s;"></div>
			</div>
		</div>`;
}