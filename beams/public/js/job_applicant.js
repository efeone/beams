frappe.ui.form.on('Job Applicant', {
    /*
     * Validate the Job Applicant against the requirements of the Job Opening.
     * This function checks if the applicant's location, qualifications,
     * experience, and skills meet the requirements specified in the Job Opening
     */
    validate: function(frm) {
        frappe.db.get_doc('Job Opening', frm.doc.job_title).then((job_opening) => {
            if (frm.doc.location !== job_opening.location) {
                frappe.msgprint(__("Applicant's location does not match the Job Opening's location."));
                frappe.validated = false;
                return;
            }
            if (frm.doc.min_education_qual && job_opening.min_education_qual) {
                let applicant_qualifications = frm.doc.min_education_qual.map(d => d.qualification);
                let job_opening_qualifications = job_opening.min_education_qual.map(d => d.qualification);
                let has_qualification = applicant_qualifications.some(qual => job_opening_qualifications.includes(qual));

                if (!has_qualification) {
                    frappe.msgprint(__("Applicant's does not meet the minimum qualification  for the Job Opening."));
                    frappe.validated = false;
                    return;
                }
            }
            if (frm.doc.min_experience < job_opening.min_experience) {
                frappe.msgprint(__("Applicant's does not meet the minimum experience  for the Job Opening."));
                frappe.validated = false;
                return;
            }
            if (job_opening.skill_proficiency && frm.doc.skill_proficiency) {
                const required_skills = job_opening.skill_proficiency.map(skill => {
                    return { skill: skill.skill, proficiency: skill.proficiency };
                });
                const applicant_skills = frm.doc.skill_proficiency.map(skill => {
                    return { skill: skill.skill, proficiency: skill.proficiency };
                });
                let missing_skills = [];
                let proficiency_mismatch = [];
                required_skills.forEach(required => {
                    const match = applicant_skills.find(applicant => applicant.skill === required.skill);
                    if (!match) {
                        // Skill is missing
                        missing_skills.push(required.skill);
                    } else if (match.proficiency < required.proficiency) {
                        // Skill is present, but proficiency is not sufficient
                        proficiency_mismatch.push(`${required.skill} (Required: ${required.proficiency}, Provided: ${match.proficiency})`);
                    }
                });
                if (missing_skills.length > 0) {
                    frappe.msgprint(__("The Applicant's does not meet the skill requirements for the Job Opening."));
                    frappe.validated = false;
                    return;
                }
                if (proficiency_mismatch.length > 0) {
                    frappe.msgprint(__("Applicant's does not meet the required proficiency levels for the following skills"));
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
    }
});
