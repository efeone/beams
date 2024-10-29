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
            }, frappe._('Create')); // Set the label of the button
        }

        if (frm.is_new()) {
            frm.toggle_display('applicant_interview_round', false);
        }
        fetch_interview_rounds(frm);
    },
    after_save: function(frm) {
        frm.toggle_display('applicant_interview_round', true);
    },
    job_title: function(frm) {
        fetch_interview_rounds(frm);
    }
  });
 /*
  * Fetches and populates interview rounds for a job applicant based on the selected job title.
  * interview rounds in the 'applicant_interview_round' child table and fetches the corresponding
  * job requisition details for the selected job title.
  */
function fetch_interview_rounds(frm) {
    if (frm.doc.job_title) {
        frm.clear_table('applicant_interview_round');
        frappe.db.get_value('Job Opening', { 'name': frm.doc.job_title }, 'job_requisition').then(r => {
            if (r.message && r.message.job_requisition) {
                const jobRequisition = r.message.job_requisition;
                frappe.db.exists('Job Requisition', jobRequisition).then(exists => {
                    if (exists) {
                        frappe.db.get_doc('Job Requisition', jobRequisition).then(job_requisition => {
                            if (job_requisition.interview_rounds && job_requisition.interview_rounds.length > 0) {
                                const existingRounds = frm.doc.applicant_interview_round.map(round => round.interview_round);

                                job_requisition.interview_rounds.forEach(round => {
                                    if (!existingRounds.includes(round.interview_round)) {
                                        const row = frm.add_child('applicant_interview_round');
                                        row.interview_round = round.interview_round;
                                    }
                                });
                                frm.refresh_field('applicant_interview_round');
                            }
                        })
                    }
                })
            }
        })
    }
}
