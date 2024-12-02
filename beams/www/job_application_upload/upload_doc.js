$(document).ready(function () {
    const { get_query_params, get_query_string } = frappe.utils;
    const applicant_id = $("#docname").val();

    // Handle file selection and reading for each file input
    var $form = $("form[id='submit_application']");
    $form.on("change", "[type='file']", function () {
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

    // Safely sanitize values
    const safeValue = (value) => value ? frappe.utils.xss_sanitise(String(value)) : "";

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
            "related_employee_rel", "professional_org", "political_org", "specialised_training", 
            "reference_taken", "was_this_position", "state_restriction"
        ];

        // Constructing the main data object
        const data = fields.reduce((obj, field) => {
            obj[field] = safeValue($(`#${field}`).val());
            return obj;
        }, { docname: applicant_id });

        // Handling checkbox values
        data.in_india = $('#in_india_checkbox').is(':checked') ? 1 : 0;
        data.abroad = $('#abroad_checkbox').is(':checked') ? 1 : 0;
        data.is_form_submitted = $('#confirm').is(':checked') ? 1 : 0;

        // Handling educational qualifications
        data.educational_qualification = [];
        $('#educational_qualification_table tbody tr').each(function () {
            const fileInput = $(this).find('input[type="file"]')[0];
            const row = {
                name_of_course_university: safeValue($(this).find('.name_of_course_university').val()),
                name_location_of_institution: safeValue($(this).find('.name_location_of_institution').val()),
                dates_attended_from: safeValue($(this).find('.dates_attended_from').val()),
                dates_attended_to: safeValue($(this).find('.dates_attended_to').val()),
                result: safeValue($(this).find('.result').val()),
                attachments: fileInput ? fileInput.filedata : null
            };
            data.educational_qualification.push(row);
        });

        // Handling professional certifications
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

        // Handling previous employment history
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

        // Handling language proficiency
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
                console.error("Error:", err);
                alert('An error occurred during submission.');
            }
        });
    });
});
