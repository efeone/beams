frappe.ui.form.on("Appointment Letter", {
    job_applicant: function(frm) {
        if (frm.doc.job_applicant) {
            frappe.db.get_value('Job Applicant', frm.doc.job_applicant, 'salutation', (r) => {
                if (r && r.salutation) {
                    frm.set_value('salutation', r.salutation);
                }
            });
        }
    }
});
