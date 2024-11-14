
$(document).ready(function () {
    const { get_query_params, get_query_string } = frappe.utils;
    const applicant_id = $("#docname").val();

    // Handle file selection and reading for each file input
    var $form = $("form[id='submit_application']");
    $form.on("change", "[type='file']", function () {
        console.log("on change");
        var $input = $(this);
        var input = $input.get(0);
        if (input.files.length) {
            input.filedata = { "files_data": [] };
            $.each(input.files, function (key, value) {
                setupReader(value, input);
            });
        }
    });
    function setupReader(file, input) {
        var reader = new FileReader();
        reader.onload = function (e) {
            input.filedata.files_data.push({
                "__file_attachment": 1,
                "filename": file.name,
                "dataurl": reader.result
            });
        };
        reader.readAsDataURL(file);
    }
    $('#submit_application').on('submit', function (event) {
        event.preventDefault();
        const fields = [
            "father_name", "applicant_name", "date_of_birth", "gender", "country", "marital_status",
            "current_address", "current_period_from", "current_period_to", "current_residence_no",
            "current_mobile_no", "permanent_address", "permanent_period_from", "permanent_period_to",
            "permanent_residence_no", "permananet_email_id", "email_id_1", "name_of_employer",
            "address_of_employer", "telephone_no", "employee_code", "current_designation",
            "current_department", "employment_period_from", "employment_period_to", "manager_name",
            "manager_contact_no", "manager_email", "duties_and_reponsibilities", "reason_for_leaving",
            "first_salary_drawn", "last_salary_drawn", "agency_details", "current_salary", "expected_salary",
            "telephone_number", "other_achievments", "position", "interviewed_location", "interviewed_date",
            "interviewed_outcome", "related_employee", "related_employee_org", "related_employee_pos",
            "related_employee_rel", "professional_org", "political_org", "specialised_training", "reference_taken", "was_this_position", "state_restriction"
        ];
        const data = fields.reduce((obj, field) => {
            obj[field] = frappe.utils.xss_sanitise($(`#${field}`).val().trim());
            return obj;
        }, { docname: applicant_id });

        data.in_india = $('#in_india_checkbox').is(':checked') ? 1 : 0;
        data.abroad = $('#abroad_checkbox').is(':checked') ? 1 : 0;
        data.is_form_submitted = $('#confirm').is(':checked') ? 1 : 0;

        data.educational_qualification = [];
        const fileReadPromises = [];

        $('#educational_qualification_table tbody tr').each(function () {
            const fileInput = $(this).find('input[type="file"]')[0];
            const row = {
                name_of_course_university: frappe.utils.xss_sanitise($(this).find('.name_of_course_university').val().trim()),
                name_location_of_institution: frappe.utils.xss_sanitise($(this).find('.name_location_of_institution').val().trim()),
                dates_attended_from: $(this).find('.dates_attended_from').val(),
                dates_attended_to: $(this).find('.dates_attended_to').val(),
                result: frappe.utils.xss_sanitise($(this).find('.result').val().trim()),
                attachments: fileInput ? fileInput.filedata : null 
            };
            data.educational_qualification.push(row);
        });
        data.professional_certification = [];
        $('#professional_qualification_table tbody tr').each(function () {
            const fileInput = $(this).find('input[type="file"]')[0];
            const row = {
                course: frappe.utils.xss_sanitise($(this).find('.course').val().trim()),
                institute_name: frappe.utils.xss_sanitise($(this).find('.institute_name').val().trim()),
                dates_attended_from: $(this).find('.dates_attended_from').val(),
                dates_attended_to: $(this).find('.dates_attended_to').val(),
                type_of_certification: frappe.utils.xss_sanitise($(this).find('.type_of_certification').val().trim()),
                subject_major: frappe.utils.xss_sanitise($(this).find('.subject_major').val().trim()),
                attachments: fileInput ? fileInput.filedata : null 
            };
            data.professional_certification.push(row);
        });
        data.prev_emp_his = [];
        $('#previous_emplyoment_history_table tbody tr').each(function () {
            const fileInput = $(this).find('input[type="file"]')[0];
            const row = {
                name_of_org: frappe.utils.xss_sanitise($(this).find('.name_of_org').val().trim()),
                prev_designation: frappe.utils.xss_sanitise($(this).find('.prev_designation').val().trim()),
                last_salary_drawn: frappe.utils.xss_sanitise($(this).find('.last_salary_drawn').val().trim()),
                name_of_manager: frappe.utils.xss_sanitise($(this).find('.name_of_manager').val().trim()),
                period_of_employment: frappe.utils.xss_sanitise($(this).find('.period_of_employment').val().trim()),
                reason_for_leaving: frappe.utils.xss_sanitise($(this).find('.reason_for_leaving').val().trim()),
                attachments: fileInput ? fileInput.filedata : null 
            };
            data.prev_emp_his.push(row);
        });
        data.language_proficiency = [];
        $('#table_3 tbody tr').each(function () {
            const row = {
                language: frappe.utils.xss_sanitise($(this).find('select[name="language"]').val().trim()),
                speak: frappe.utils.xss_sanitise($(this).find('input[name^="speak"]:checked').val() || 0),
                read: frappe.utils.xss_sanitise($(this).find('input[name^="read"]:checked').val() || 0),
                write: frappe.utils.xss_sanitise($(this).find('input[name^="write"]:checked').val() || 0)
            };
            if (row.language) {
                data.language_proficiency.push(row);
            }
        });
        // Submit the form data with files included
        frappe.call({
            method: "beams.www.job_application_upload.upload_doc.update_register_form",
            args: {
                data: JSON.stringify(data),
                docname: applicant_id
            },
            callback: function (r) {
                alert(r.message === "success" ? 'Job Applicant updated successfully!' : 'Submission completed.');
            },
            error: function (err) {
                console.log("Error:", err);
                alert('An error occurred during submission.');
            }
        });
    });
});

