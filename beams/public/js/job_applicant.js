
frappe.ui.form.on('Job Applicant', {
    /*
     * Validate the Job Applicant against the requirements of the Job Opening.
     * This function checks if the applicant's location, qualifications,
     * experience, and skills meet the requirements specified in the Job Opening
     */
    validate: function(frm) {
        frappe.db.get_doc('Job Opening', frm.doc.job_title).then((job_opening) => {
            if (frm.doc.location !== job_opening.location) {
                frappe.msgprint("Applicant's location does not match the Job Opening's location.");
                frappe.validated = false;
                return;
            }
            if (frm.doc.min_education_qual && job_opening.min_education_qual) {
                let applicant_qualifications = frm.doc.min_education_qual.map(d => d.qualification);
                let job_opening_qualifications = job_opening.min_education_qual.map(d => d.qualification);
                let has_qualification = applicant_qualifications.some(qual => job_opening_qualifications.includes(qual));

                if (!has_qualification) {
                    frappe.msgprint("Applicant's does not meet the minimum qualification  for the Job Opening.");
                    frappe.validated = false;
                    return;
                }
            }
            if (frm.doc.min_experience < job_opening.min_experience) {
                frappe.msgprint("Applicant's does not meet the minimum experience  for the Job Opening.");
                frappe.validated = false;
                return;
            }
            if (job_opening.skill_proficiency && frm.doc.skill_proficiency) {
                const requiredSkills = job_opening.skill_proficiency.map(skill => {
                    return { skill: skill.skill, proficiency: skill.proficiency };
                });
                const applicantSkills = frm.doc.skill_proficiency.map(skill => {
                    return { skill: skill.skill, proficiency: skill.proficiency };
                });
                let missingSkills = [];
                let proficiencyMismatch = [];
                requiredSkills.forEach(required => {
                    const match = applicantSkills.find(applicant => applicant.skill === required.skill);
                    if (!match) {
                        // Skill is missing
                        missingSkills.push(required.skill);
                    } else if (match.proficiency < required.proficiency) {
                        // Skill is present, but proficiency is not sufficient
                        proficiencyMismatch.push(`${required.skill} (Required: ${required.proficiency}, Provided: ${match.proficiency})`);
                    }
                });
                if (missingSkills.length > 0) {
                    frappe.msgprint("The Applicant's does not meet the skill requirements for the Job Opening.");
                    frappe.validated = false;
                    return;
                }
                if (proficiencyMismatch.length > 0) {
                    frappe.msgprint("Applicant's does not meet the required proficiency levels for the following skills");
                    frappe.validated = false;
                    return;
                }
            }
        });
    }
});
