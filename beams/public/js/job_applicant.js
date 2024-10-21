frappe.ui.form.on('Job Applicant', {
    /*
     * Validate the Job Applicant against the requirements of the Job Opening.
     * This function checks if the applicant's location, qualifications,
     * experience, and skills meet the requirements specified in the Job Opening
     */
     validate: function(frm) {
      frappe.db.get_doc('Job Opening', frm.doc.job_title).then((job_opening) => {
          if (frm.doc.location !== job_opening.location) {
              frappe.msgprint(__("Applicant location does not match the desired location {0}").format(job_opening.location));
              frappe.validated = false;
              return;
          }
          if (frm.doc.min_education_qual && job_opening.min_education_qual) {
              const applicant_qualification = frm.doc.min_education_qual;
              const job_opening_qualifications = job_opening.min_education_qual.map(d => d.qualification);

              if (!job_opening_qualifications.includes(applicant_qualification)) {
                  const required_qualifications = job_opening_qualifications.join(", ");
                  frappe.msgprint(__("Applicant does not match Educational qualifications required: {0}").format(required_qualifications));
                  frappe.validated = false;
                  return;
              }
          }
          if (frm.doc.min_experience < job_opening.min_experience) {
              frappe.msgprint(__("Applicant does not meet the Required experience: {0} years").format(job_opening.min_experience));
              frappe.validated = false;
              return;
          }
          if (job_opening.skill_proficiency && frm.doc.skill_proficiency) {
              const required_skills = job_opening.skill_proficiency.map(skill => skill.skill);
              const applicant_skills = frm.doc.skill_proficiency.map(skill => skill.skill);
              const missing_skills = required_skills.filter(skill => !applicant_skills.includes(skill));

              if (missing_skills.length > 0) {
                  const required_skills_list = required_skills.join(", ");
                  frappe.msgprint(__("The Applicant does not meet the Required skills: {0}.").format(required_skills_list));
                  frappe.validated = false;
                  return;
              }
          }
      });
     },

    refresh: function(frm) {
        // Check if the current form is not a new record
        if (!frm.is_new()) {
            // Add a custom button labeled 'Local Enquiry Report'
            frm.add_custom_button(frappe._('Local Enquiry Report'), function() {
                // Call the backend method to create a local enquiry report
                frappe.call({
                    method: "beams.beams.custom_scripts.job_applicant.job_applicant.create_local_enquiry",
                    args: {
                        doc_name: frm.doc.name  // Pass the name of the Job Applicant to the method
                    },
                    callback: function(r) {
                        // Check if a report was successfully created
                        if (r.message) {
                            // Notify the user that the report was created successfully
                            frappe.msgprint(__('Local Enquiry Report created: {0}', [r.message]));
                            // Redirect to the Local Enquiry Report form
                            frappe.set_route('Form', 'Local Enquiry Report', r.message);
                        } else {
                            // Notify the user that the report already exists
                            frappe.msgprint(__('Report already exists.'));
                        }
                    },
                });
            }, frappe._('Create'));

            // Add a custom button for sending a magic link
            frm.add_custom_button(__('Send Magic Link'), function() {
                frappe.confirm(
                    'Are you sure you want to send the magic link to the candidate?',
                     function() {
                        let applicant_name_value = frm.doc.name;
                        frappe.call({
                            method: "beams.beams.custom_scripts.job_applicant.job_applicant.send_magic_link",
                            args: {
                                applicant_name: applicant_name_value
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.msgprint("Magic link has been sent to the candidate.");
                                }
                            }
                        });
                      }
                  );
              }, __('Create'));
          }
      }
  });
