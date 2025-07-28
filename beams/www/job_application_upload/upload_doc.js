$(document).ready(function () {
	$('.navbar').hide();
	$('.web-footer').hide();
	const { get_query_params, get_query_string } = frappe.utils;
	const applicant_id = $('#docname').val();

	// Handle file selection and reading for each file input
	var $form = $('form[id="submit_application"]');
	$form.on('change', '[type="file"]', function () {
		var $input = $(this);
		var input = $input.get(0);
		if (input.files.length) {
			input.filedata = { 'files_data': [] };
			$.each(input.files, function (key, value) {
				setupReader(value, input);
			});
		}
	});

	function setupReader(file, input) {
		var reader = new FileReader();
		reader.onload = function (e) {
			input.filedata.files_data.push({
				'__file_attachment': 1,
				'filename': file.name,
				'dataurl': reader.result
			});
		};
		reader.readAsDataURL(file);
	}

	// Safely sanitize values
	const safeValue = (value) => value ? frappe.utils.xss_sanitise(String(value)) : '';
	const date_of_birth = safeValue($('#date_of_birth').val());
	const interviewed_date = safeValue($('#interviewed_date').val());

	$form.on('submit', function (event) {
		event.preventDefault();

		const currentEmployerTab = document.getElementById("currentEmployerTab");

		// Only validate if currentEmployerTab is visible
		if (currentEmployerTab && currentEmployerTab.style.display !== "none") {
			const managerEmail = safeValue($('#manager_email').val());
			const managerPhone = safeValue($('#manager_contact_no').val());

			const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
			const phoneRegex = /^\d{10}$/;

			if (!managerEmail) {
				alert('Manager Email is required.');
				return false;
			}

			if (!emailRegex.test(managerEmail)) {
				alert('Please enter a valid manager email address.');
				return false;
			}

			if (!managerPhone) {
				alert('Contact No is required.');
				return false;
			}

			if (!phoneRegex.test(managerPhone)) {
				alert('Please enter a valid 10-digit mobile number for Manager Contact No.');
				return false;
			}
		}

		const aadhaarField = document.getElementById('aadhaar_field');
		const aadhaarInput = document.getElementById('aadhaar_number_input');

		const isAadhaarVisible = aadhaarField && aadhaarField.style.display !== "none";
		const aadhaarNumber = aadhaarInput ? safeValue($(aadhaarInput).val()) : '';

		if (isAadhaarVisible) {
			if (!aadhaarNumber || aadhaarNumber.length !== 12 || !/^\d{12}$/.test(aadhaarNumber)) {
				alert('Please enter a valid 12-digit Aadhaar number.');
				return false;
			}
		}

		event.preventDefault();
		const fields = [
			'father_name', 'applicant_name', 'date_of_birth', 'gender', 'country', 'marital_status',
			'current_house_no','current_city','current_perm_post_office','current_street','current_district',
			'current_pin','current_locality','current_state','period_years','current_period_months',
			'permanent_house_no','permanent_city','permanent_perm_post_office','permanent_street',
			'permanent_district','permanent_pin','permanent_locality','permanent_state', 'email_id',
			'aadhaar_number_input', 'name_of_employer','current_department','current_designation','reports_to',
			'manager_name','manager_contact_no','manager_email','reference_taken',
			'address_of_employer', 'duties_and_reponsibilities', 'reason_for_leaving',
			'agency_details', 'current_salary', 'expected_salary',
			'other_achievments', 'position', 'interviewed_location', 'interviewed_date',
			'interviewed_outcome', 'related_employee', 'related_employee_org', 'related_employee_pos',
			'related_employee_rel', 'professional_org', 'political_org', 'specialised_training',
			'reference_taken', 'was_this_position', 'state_restriction', 'achievements_checkbox',
			'interviewed_before_checkbox', 'related_to_employee_checkbox', 'professional_org_checkbox',
			'political_org_checkbox', 'specialised_training_checkbox','additional_comments'
		];

		const first_name = safeValue($('#first_name').val());
		const last_name = safeValue($('#last_name').val());
		const full_name = `${first_name} ${last_name}`.trim();
		const email = safeValue($('#email').val());

		const data = fields.reduce((obj, field) => {
			obj[field] = safeValue($(`#${field}`).val());
			return obj;
		}, {
			docname: applicant_id,
			date_of_birth: date_of_birth,
			interviewed_date: interviewed_date
		});

		data.in_india = $('#in_india_checkbox').is(':checked') ? 1 : 0;
		data.abroad = $('#abroad_checkbox').is(':checked') ? 1 : 0;
		data.is_form_submitted = $('#confirm').is(':checked') ? 1 : 0;

		data.education_qualification = [];
		$('#education_qualification_table tbody tr').each(function () {
			const fileInput = $(this).find('input[type="file"]')[0];
			const row = {
				course: safeValue($(this).find('.course').val()),
				name_of_school_college: safeValue($(this).find('.name_of_school_college').val()),
				name_of_universityboard_of_exam: safeValue($(this).find('.name_of_universityboard_of_exam').val()),
				dates_attended_from: safeValue($(this).find('.dates_attended_from').val()),
				dates_attended_to: safeValue($(this).find('.dates_attended_to').val()),
				result: safeValue($(this).find('.result').val()),
				attachments: fileInput ? fileInput.filedata : null
			};
			data.education_qualification.push(row);
		});

		data.professional_certification = [];
		$('#professional_qualification_table tbody tr').each(function () {
			const fileInput = $(this).find('input[type="file"]')[0];
			const row = {
				course: safeValue($(this).find('.course').val()),
				institute_name: safeValue($(this).find('.institute_name').val()),
				dates_attended_from: safeValue($(this).find('.dates_attended_from').val()),
				dates_attended_to: safeValue($(this).find('.dates_attended_to').val()),
				type_of_certification: safeValue($(this).find('.type_of_certification').val()),
				subject_major: safeValue($(this).find('.subject_major').val()),
				attachments: fileInput ? fileInput.filedata : null
			};
			data.professional_certification.push(row);
		});

		data.prev_emp_his = [];
		$('#previous_emplyoment_history_table tbody tr').each(function () {
			const fileInput = $(this).find('input[type="file"]')[0];
			const row = {
				name_of_org: safeValue($(this).find('.name_of_org').val()),
				prev_designation: safeValue($(this).find('.prev_designation').val()),
				last_salary_drawn: safeValue($(this).find('.last_salary_drawn').val()),
				name_of_manager: safeValue($(this).find('.name_of_manager').val()),
				period_of_employment: safeValue($(this).find('.period_of_employment').val()),
				reason_for_leaving: safeValue($(this).find('.reason_for_leaving').val()),
				attachments: fileInput ? fileInput.filedata : null
			};
			data.prev_emp_his.push(row);
		});

		data.language_proficiency = [];
		$('#table_3 tbody tr').each(function () {
			const row = {
				language: safeValue($(this).find('select[name="language"]').val()),
				speak: safeValue($(this).find('input[name^="speak"]:checked').val() || 0),
				read: safeValue($(this).find('input[name^="read"]:checked').val() || 0),
				write: safeValue($(this).find('input[name^="write"]:checked').val() || 0)
			};
			if (row.language) {
				data.language_proficiency.push(row);
			}
		});

		const payslipFields = ['payslip_month_1', 'payslip_month_2', 'payslip_month_3'];
		payslipFields.forEach(field => {
			const fileInput = $(`#${field}`)[0];
			if (fileInput && fileInput.files.length) {
				data[field] = fileInput.filedata;
			} else {
				data[field] = null;
			}
		});

		frappe.call({
			method: 'beams.www.job_application_upload.upload_doc.update_register_form',
			args: {
				form_data: JSON.stringify(data),
				docname: applicant_id
			},
			callback: function (r) {
				alert(r.message === 'success' ? 'Job Applicant updated successfully!' : 'Submission completed.');

				const confirmCheckbox = $('#confirm');
				const errorMessage = $('#error-message');

				if (confirmCheckbox.is(':checked')) {
					errorMessage.hide();
					window.location.href = '/application_success/success.html';
				} else {
					errorMessage.show(); // Show red message if checkbox not ticked
				}
			},
			error: function (err) {
				alert('An error occurred during submission.');
			}
		});
	});
});
