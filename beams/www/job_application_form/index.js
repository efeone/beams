$(document).ready(function () {
	const file_input = document.getElementById('resume_attachment');
	const placeholder = document.querySelector('.placeholder');
	let max_resume_size_kb = 10240; // Default to 10 MB

	// Click to open file dialog
	placeholder.addEventListener('click', (event) => {
		event.preventDefault();
		file_input.click();  // Trigger the file input click
	});

	// Handle file selection
	file_input.addEventListener('change', function () {
		const file_names = Array.from(this.files).map(file => file.name).join(", ");
		placeholder.textContent = file_names ? `Selected: ${file_names}` : 'No file chosen';

		if (this.files.length > 0) {
			this.file_data = { "files_data": [] }; // Reset file_data
			process_files(this);                    // Process selected files
		}
	});

	function process_files(input) {
		window.file_reading = true;
		let files_processed = 0;
		const total_files = input.files.length;

		$.each(input.files, function (key, file) {
			setup_reader(file, input, () => {
				files_processed++;
				if (files_processed === total_files) {
					window.file_reading = false;
				}
			});
		});
	}

	function setup_reader(file, input, callback) {
		const file_reader = new FileReader();
		file_reader.onload = function () {
			input.file_data.files_data.push({
				"__file_attachment": 1,
				"filename": file.name,
				"dataurl": file_reader.result
			});
			callback();
		};
		file_reader.readAsDataURL(file);
	}

	$('#employment_form').on('submit', function (event) {
		event.preventDefault();

		if (window.file_reading) {
			alert("Please wait, files are still being processed!");
			return;
		}

		const applicant_name = frappe.utils.xss_sanitise($("#applicant_name").val().trim());
		const email_id = frappe.utils.xss_sanitise($("#email_id").val().trim());
		const phone_number = frappe.utils.xss_sanitise($("#phone_number").val().trim());
		const min_experience = frappe.utils.xss_sanitise($("#min_experience").val().trim());
		const min_education_qual = frappe.utils.xss_sanitise($("#min_education_qual").val().trim());
		const job_title = frappe.utils.xss_sanitise($("#job_title").val().trim());
		const location = frappe.utils.xss_sanitise($("#location").val().trim());
		
		// Validates the email address format before form submission.
		const email_pattern = /^[a-zA-Z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/;
		if (!email_pattern.test(email_id)) {
			alert("Please enter a valid email address.");
			return;
		}

		// Ensure file data is properly assigned
		const resume_attachment = file_input.file_data ? file_input.file_data.files_data : [];

		if (resume_attachment.length === 0) {
			alert("Please upload a resume before submitting.");
			return;
		}
		// Fetch resume_size from Beams HR Settings (in KB)
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Beams HR Settings",
				fieldname: "resume_size"
			},
			callback: function (response) {
				if (response.message && response.message.resume_size) {
					max_resume_size_kb = parseFloat(response.message.resume_size);
				}
				// Resume size validation
				if (max_resume_size_kb > 0) {
					const oversized_file = Array.from(file_input.files).find(file => (file.size / 1024) > max_resume_size_kb);
					if (oversized_file) {
						alert(`The file "${oversized_file.name}" exceeds the maximum allowed size of ${max_resume_size_kb} KB.`);
						return;
					}
				}

				// Collect skills data
				const skills = get_skills_data();

				frappe.call({
					method: "beams.www.job_application_form.index.create_job_applicant",
					args: {
						"applicant_name": applicant_name,
						"email_id": email_id,
						"phone_number": phone_number,
						"min_experience": min_experience,
						"min_education_qual": min_education_qual,
						"job_title": job_title,
						"location": location,
						"resume_attachment": JSON.stringify(resume_attachment), // Convert to JSON string
						"skill_proficiency": JSON.stringify(skills) // Ensure skill_proficiency is also a JSON string
					},
					callback: function (response) {
						alert("Your Application has been submitted!");
						window.location.href = '/job_portal';
					},
					error: function (error) {
						alert('Something went wrong, Please try again');
					}
				});
			}
		});

	});
});

// Extract skills data
function get_skills_data() {
	let skills = [];
	$('#skills tbody tr').each(function () {
		const row = {
			skill: $(this).find('select[name="skill"]').val(),
			rating: $(this).find('input[name^="rating"]:checked').val() || 0,
		};
		if (row.skill) {
			skills.push(row);
		}
	});
	return skills;
}
