$(document).ready(function () {
    const fileInput = document.getElementById('resume_attachment');
    const placeholder = document.querySelector('.placeholder');

    // Click to open file dialog
    placeholder.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent any default behavior
        fileInput.click();  // Trigger the file input click
    });

    // Handle file selection
    fileInput.addEventListener('change', function () {
        const fileNames = Array.from(this.files).map(file => file.name).join(", ");
        placeholder.textContent = fileNames ? `Selected: ${fileNames}` : 'No file chosen';

        if (this.files.length > 0) {
            this.filedata = { "files_data": [] }; // Reset filedata
            processFiles(this);                    // Process selected files
        }
    });

    function processFiles(input) {
        window.file_reading = true;
        let filesProcessed = 0;
        const totalFiles = input.files.length;

        $.each(input.files, function (key, file) {
            setupReader(file, input, () => {
                filesProcessed++;
                if (filesProcessed === totalFiles) {
                    window.file_reading = false;
                    console.log("All files processed");
                }
            });
        });
    }

    function setupReader(file, input, callback) {
        const reader = new FileReader();
        reader.onload = function () {
            input.filedata.files_data.push({
                "__file_attachment": 1,
                "filename": file.name,
                "dataurl": reader.result
            });
            callback();
        };
        reader.readAsDataURL(file);
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

        // Ensure file data is properly assigned
        const resume_attachment = fileInput.filedata ? fileInput.filedata.files_data : [];

        if (resume_attachment.length === 0) {
            alert("Please upload a resume before submitting.");
            return;
        }

        // Collect skills data
        const skills = get_skills_data();

        // Send data to backend
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
                window.location.href = '/job_portal';
            },
            error: function (err) {
                alert('Something went wrong, Please try again');
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