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
		const aadhaarField = document.getElementById('aadhaar_field');
		const aadhaarInput = document.getElementById('aadhaar_number_input');

		const isAadhaarVisible = aadhaarField && aadhaarField.style.display !== "none";
		const aadhaarNumber = aadhaarInput ? safeValue($(aadhaarInput).val()) : '';

		function focusFieldInTab(fieldSelector, tabIndex) {
		// Switch to the correct tab
		showTab(tabIndex);

		// Wait for tab content to render, then scroll and focus
		setTimeout(() => {
			const field = $(fieldSelector);
			if (field.length) {
				field.focus();
				$('html, body').animate({
					scrollTop: field.offset().top - 100
				}, 300);
			}
		}, 200);
	}

	const fieldTabMap = {
    // Personal Information tab (index 0)
    '#aadhaar_number_input': 0,
    '#current_city': 0,
	'#current_pin': 0,
	'#phone_number': 0,
	'#date_of_birth': 0,
	'#interviewed_date': 0,
	'#current_perm_post_office': 0,
	'#current_street': 0,
	'#current_house_no': 0,
	'#current_district': 0,
	'#current_state': 0,
	'#current_locality': 0,
    // Current Employer tab (index 1)
    '#manager_email': 1,
	'#manager_name': 1,
    '#manager_contact_no': 1,
    '#payslip_month_1': 1,

	};

		const date_of_birth = safeValue($('#date_of_birth').val());
			if (!date_of_birth) {
				showError('Please enter a valid date of birth.');
				focusFieldInTab('#date_of_birth', fieldTabMap['#date_of_birth']);
				return false;
			}

		if (isAadhaarVisible) {
			if (!aadhaarNumber || aadhaarNumber.length !== 12 || !/^\d{12}$/.test(aadhaarNumber)) {
				showError('Please enter a valid 12-digit Aadhaar number.');
				focusFieldInTab('#aadhaar_number_input', fieldTabMap['#aadhaar_number_input']);				return false;
			}
		}

		window.showTab = showTab;

		const phoneNumber = safeValue($('#phone_number').val());
		const phoneNumberRegex = /^\d{10}$/;
		const current_pin = safeValue($('#current_pin').val());
		const pinRegex = /^\d{6}$/;
		const current_house_no = safeValue($('#current_house_no').val());
		if (!current_house_no) {
			showError('Please enter a valid house number.');
			focusFieldInTab('#current_house_no', fieldTabMap['#current_house_no']);
			return false;
		}
		const current_city = safeValue($('#current_city').val());
		if (!current_city) {
			showError('Please enter a valid city.');
			focusFieldInTab('#current_city', fieldTabMap['#current_city']);
			return false;
		}
		const current_perm_post_office = safeValue($('#current_perm_post_office').val());
		if (!current_perm_post_office) {
			showError('Please enter a valid post office.');
			focusFieldInTab('#current_perm_post_office', fieldTabMap['#current_perm_post_office']);
			return false;
		}
		const current_street = safeValue($('#current_street').val());
		if (!current_street ) {
			showError('Please enter a valid street.');
			focusFieldInTab('#current_street', fieldTabMap['#current_street']);
			return false;
		}
		const current_district = safeValue($('#current_district').val());
		if (!current_district) {
			showError('Please enter a valid district.');
			focusFieldInTab('#current_district', fieldTabMap['#current_district']);
			return false;
		}

		if (!current_pin) {
			showError('Please enter a valid 6-digit PIN.');
			focusFieldInTab('#current_pin', fieldTabMap['#current_pin']);
			return false;
		}

		if (!pinRegex.test(current_pin)) {
			showError('Please enter a valid 6-digit PIN.');
			focusFieldInTab('#current_pin', fieldTabMap['#current_pin']);
			return false;
		}

		const current_locality = safeValue($('#current_locality').val());
		if (!current_locality) {
			showError('Please enter a valid locality.');
			focusFieldInTab('#current_locality', fieldTabMap['#current_locality']);
			return false;
		}

		const current_state = safeValue($('#current_state').val());
		if (!current_state) {
			showError('Please enter a valid state.');
			focusFieldInTab('#current_state', fieldTabMap['#current_state']);
			return false;
		}

		if (!phoneNumber || !phoneNumberRegex.test(phoneNumber)) {
			showError('Please enter a valid 10-digit mobile number.');
			focusFieldInTab('#phone_number', fieldTabMap['#phone_number']);
			return false;
		}

        const resultpercentage = safeValue($('#results_1').val());  // Sanitize input value
        // Check if the value is greater than 100
        if (resultpercentage && parseFloat(resultpercentage) > 100) {
            showError('Please enter a percentage less than or equal to 100.');  // Error message if value > 100
            focusFieldInTab('#results_1', fieldTabMap['#results_1']);  // Focus on the input field
            event.preventDefault();  // Prevent form submission
            return false;  // Stop further actions
        }

		// Only validate if currentEmployerTab is visible
		if (currentEmployerTab && currentEmployerTab.style.display !== "none") {
			const managerEmail = $('#manager_email').val();
			const managerName = safeValue($('#manager_name').val());
			const managerPhone = safeValue($('#manager_contact_no').val());
			const payslip_month_1= safeValue($('#payslip_month_1').val());
			const payslip_month_2= safeValue($('#payslip_month_2').val());
			const payslip_month_3= safeValue($('#payslip_month_3').val());

			const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
			const phoneRegex = /^\d{10}$/;

			if (!managerName) {
				showError('Manager Name is required.');
				focusFieldInTab('#manager_name', 1);
				return false;
			}

			if (!managerPhone) {
				showError(' Manager Contact Number is required.');
				focusFieldInTab('#manager_contact_no', 1);
				return false;
			}

			if (!phoneRegex.test(managerPhone)) {
				showError('Please enter a valid 10-digit mobile number for Manager Contact No.');
				focusFieldInTab('#manager_contact_no', 1);
				return false;
			}

			if (!managerEmail) {
				showError('Manager Email is required.');
				focusFieldInTab('#manager_email', 1);
				return false;
			}

			if (!emailRegex.test(managerEmail)) {
				showError('Please enter a valid manager email address.');
				focusFieldInTab('#manager_email', 1);
				return false;
			}

			if (!payslip_month_1 || !payslip_month_2 || !payslip_month_3) {
				showError('Please upload last 3 months payslips.');
				focusFieldInTab('#payslip_month_1', 1);
				return false;
			}
			const language = safeValue($('select[name="language"]').val()).trim();
			const speak = $('input[name="speak"]:checked').val() || '';
			const read = $('input[name="read"]:checked').val() || '';
			const write = $('input[name="write"]:checked').val() || '';

			//  Achievements (Professional / Awards)
			if ($('#achievements_checkbox').is(':checked')) {
				if (!safeValue($('#other_achievments').val().trim())) {
					showError('Please provide details of your achievements or awards.');
					focusFieldInTab('#other_achievments', 2);
					return false;
				}
			}

			//  Interviewed Before
			if ($('#interviewed_before_checkbox').is(':checked')) {
				const interviewFields = ['#position', '#interviewed_location', '#interviewed_date', '#interviewed_outcome'];
				for (let field of interviewFields) {
					if (!safeValue($(field).val().trim())) {
						showError('Please fill all interview details.');
						focusFieldInTab(field, 2);
						return false;
					}
				}
			}
			if (!language && (speak !== '' || read !== '' || write !== '')) {
				showError('Please select a language.');
				focusFieldInTab('select[name="language"]', 2);
				return false;
			}

			// --- Checkbox-driven mandatory validation ---

			//  Related to employee
			if ($('#related_to_employee_checkbox').is(':checked')) {
				const relatedFields = ['#related_employee', '#related_employee_org', '#related_employee_pos'];
				for (let field of relatedFields) {
					if (!safeValue($(field).val().trim())) {
						showError('Please fill all related employee details.');
						focusFieldInTab(field, 2); // Personal Info tab (adjust if needed)
						return false;
					}
				}
			}

			//  Professional Organization
			if ($('#professional_org_checkbox').is(':checked')) {
				if (!safeValue($('#professional_org').val().trim())) {
					showError('Please provide details of the Professional Organization.');
					focusFieldInTab('#professional_org', 2);
					return false;
				}
			}

			//  Political Organization
			if ($('#political_org_checkbox').is(':checked')) {
				if (!safeValue($('#political_org').val().trim())) {
					showError('Please provide details of the Political Organization.');
					focusFieldInTab('#political_org', 2);
					return false;
				}
			}

			//  Specialized Training
			if ($('#specialised_training_checkbox').is(':checked')) {
				if (!safeValue($('#specialised_training').val().trim())) {
					showError('Please provide details of the Specialized Training.');
					focusFieldInTab('#specialised_training', 2);
					return false;
				}
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
			'address_of_employer', 'duties_and_responsibilities', 'reason_for_leaving',
			'agency_details', 'current_salary', 'expected_salary',
			'other_achievments', 'position', 'interviewed_location', 'interviewed_date',
			'interviewed_outcome', 'related_employee', 'related_employee_org', 'related_employee_pos',
			'related_employee_rel', 'professional_org', 'political_org', 'specialised_training',
			'reference_taken', 'was_this_position', 'state_restriction', 'achievements_checkbox',
			'interviewed_before_checkbox', 'related_to_employee_checkbox', 'professional_org_checkbox',
			'political_org_checkbox', 'specialised_training_checkbox','additional_comments','phone_number'
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

		$('#form-error').hide();
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
				showError('An error occurred during submission.');
			}
		});
	});
});