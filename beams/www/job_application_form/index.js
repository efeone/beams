$(document).ready(function () {
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
        const resume_attachment = frappe.utils.xss_sanitise($("#resume_attachment").val().trim());

        // Define skill array to capture skills and ratings
        const skill = [];
        $("#skill_proficiency tbody tr").each(function () {
            const skill_name = $(this).find('select[name="language"]').val();
            const rating = $(this).find('input[type="radio"]:checked').val();
            if (skill_name && rating) {
                skill.push({ skill: skill_name, rating: rating });
            }
        });

        // Send form data to backend
        frappe.call({
            method: "beams.www.job_application_form.index.submit_job_application",
            args: {
                "applicant_name": applicant_name,
                "email_id": email_id,
                "phone_number": phone_number,
                "min_experience": min_experience,
                "min_education_qual": min_education_qual,
                "job_title": job_title,
                "location": location,
                "resume_attachment": resume_attachment,
                "skill_proficiency": JSON.stringify(skill)  // Pass skill array as JSON
            },
            callback: function (r) {
                if (r.message === "Job application submitted successfully") {
                    alert('Job application submitted successfully!');
                } else {
                    alert('Job application submitted successfully!');
                }
            },
            error: function (err) {
                alert('Job application submitted successfully!');
            }
        });
    });

    document.getElementById('add-row-lang').addEventListener('click', function () {
        const table = document.getElementById('skill_proficiency').getElementsByTagName('tbody')[0];
        const rowCount = table.rows.length + 1;
        const row = table.insertRow();

        row.innerHTML = `
      <td>${rowCount}</td>
      <td>
          <select id="skill_${rowCount}" name="language" style="background-color: #fff;">
              <option value="">Select Skill</option>
              {% for skill in skill %}
                  <option value="{{ skill.name }}">{{ skill.skill_name }}</option>
              {% endfor %}
          </select>
      </td>
      <td>
          <div class="star-rating">
              <input type="radio" id="speak-${rowCount}-5" name="speak_${rowCount}" value="5">
              <label for="speak-${rowCount}-5">&#9733;</label>
              <input type="radio" id="speak-${rowCount}-4" name="speak_${rowCount}" value="4">
              <label for="speak-${rowCount}-4">&#9733;</label>
              <input type="radio" id="speak-${rowCount}-3" name="speak_${rowCount}" value="3">
              <label for="speak-${rowCount}-3">&#9733;</label>
              <input type="radio" id="speak-${rowCount}-2" name="speak_${rowCount}" value="2">
              <label for="speak-${rowCount}-2">&#9733;</label>
              <input type="radio" id="speak-${rowCount}-1" name="speak_${rowCount}" value="1">
              <label for="speak-${rowCount}-1">&#9733;</label>
          </div>
      </td>`;
    });
});