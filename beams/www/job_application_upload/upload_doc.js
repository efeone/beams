$(document).ready(function () {
  $('#submit-application').on('submit', function (event) {
    event.preventDefault();

    if (!$('#confirm').is(':checked')) {
      $('#error-message').show();
      return;
    } else {
      $('#error-message').hide();
    }

    const first_name = frappe.utils.xss_sanitise($("#first_name").val().trim());
    const last_name = frappe.utils.xss_sanitise($("#last_name").val().trim());
    const father_name = frappe.utils.xss_sanitise($("#father_name").val().trim());
    const date_of_birth = frappe.utils.xss_sanitise($("#date_of_birth").val().trim());
    const gender = frappe.utils.xss_sanitise($("#gender").val().trim());
    const marital_status = frappe.utils.xss_sanitise($("#marital_status").val().trim());
    const current_address = frappe.utils.xss_sanitise($("#current_address").val().trim());
    const current_period_from = frappe.utils.xss_sanitise($("#current_period_from").val().trim());
    const current_period_to = frappe.utils.xss_sanitise($("#current_period_to").val().trim());
    const current_residence_no = frappe.utils.xss_sanitise($("#current_residence_no").val().trim());
    const current_mobile_no = frappe.utils.xss_sanitise($("#current_mobile_no").val().trim());
    const permanent_address = frappe.utils.xss_sanitise($("#permanent_address").val().trim());
    const permanen_period_from = frappe.utils.xss_sanitise($("#permanen_period_from").val().trim());
    const permanent_period_to = frappe.utils.xss_sanitise($("#permanent_period_to").val().trim());
    const permanent_residence_no = frappe.utils.xss_sanitise($("#permanent_residence_no").val().trim());
    const permanent_email_id = frappe.utils.xss_sanitise($("#permanent_email_id").val().trim());
    const email_id_1 = frappe.utils.xss_sanitise($("#email_id_1").val().trim());

    frappe.call({
      method: "beams.beams.www.job_application_upload.upload_doc.create_job_applicant",
      args: {
        "first_name": first_name,
        "last_name": last_name,
        "father_name": father_name,
        "date_of_birth": date_of_birth,
        "gender": gender,
        "marital_status": marital_status,
        "current_address": current_address,
        "current_period_from": current_period_from,
        "current_period_to": current_period_to,
        "current_residence_no": current_residence_no,
        "current_mobile_no": current_mobile_no,
        "permanent_address": permanent_address,
        "permanen_period_from": permanen_period_from,
        "permanent_period_to": permanent_period_to,
        "permanent_residence_no": permanent_residence_no,
        "permanent_email_id": permanent_email_id,
        "email_id_1": email_id_1
      },
      callback: function (r) {
        if (r.message === "success") {
          alert('Job Applicant created successfully!');
        } else {
          alert('An error occurred. Please try again.');
        }
      },
      error: function (err) {
        alert('An error occurred during submission.');
      }
    });
  });
});
