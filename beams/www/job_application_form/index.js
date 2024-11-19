$(document).ready(function () {
    const fileInput = document.getElementById('resume_attachment');
    const placeholder = document.querySelector('.placeholder');

    placeholder.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        const fileName = fileInput.files.length > 0 ? fileInput.files[0].name : 'No file chosen';
        placeholder.textContent = `Selected: ${fileName}`;
    });

    var $form = $("form[id='employment_form']")
    $form.on("change", "[type='file']", function () {
        var $input = $(this);
        var input = $input.get(0);
        if (input.files.length) {
            input.filedata = { "files_data": [] };
            window.file_reading = true;
            $.each(input.files, function (key, value) {
                setupReader(value, input);
            });
            window.file_reading = false;
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

    $('#employment_form').on('submit', function (event) {
        event.preventDefault();

        // Gather form data and sanitize inputs
        const applicant_name = frappe.utils.xss_sanitise($("#applicant_name").val().trim());
        const email_id = frappe.utils.xss_sanitise($("#email_id").val().trim());
        const phone_number = frappe.utils.xss_sanitise($("#phone_number").val().trim());
        const min_experience = frappe.utils.xss_sanitise($("#min_experience").val().trim());
        const min_education_qual = frappe.utils.xss_sanitise($("#min_education_qual").val().trim());
        const job_title = frappe.utils.xss_sanitise($("#job_title").val().trim());
        const location = frappe.utils.xss_sanitise($("#location").val().trim());
        var resume_attachment = $('#resume_attachment').prop('filedata')

        const skills = get_skills_data();

        // Send form data to backend
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
                "resume_attachment": resume_attachment,
                "skill_proficiency": skills
            },
            callback: function (r) {
                alert("Your Application has been submitted!");
                window.location.reload()
            },
            error: function (err) {
                alert('Something went wrong, Please try again');
            }
        });
    });
});

function deleteRow(button) {
    var row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function get_skills_data() {
    let skills = [];
    $('#skills tbody tr').each(function () {
        const row = {
            language: $(this).find('select[name="skill"]').val(),
            rating: $(this).find('input[name^="rating"]:checked').val() || 0,
        };
        if (row.language) {
            skills.push(row);
        }
    });
    return skills
}