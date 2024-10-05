
frappe.ui.form.on('Job Requisition', {
  refresh: function(frm) {
        frm.set_df_property('status', 'read_only', 1);
    },
     /*
     * This function triggers when the designation field is changed.
     * It sets a filter for the Job Description Template based on the selected designation.
     */
    designation: function(frm) {
        frm.set_query('job_description_template', function() {
            return {
                filters: {
                    'designation': frm.doc.designation
                }
            };
        });
        // Refresh the Job Description Template field to apply the new filter
        frm.refresh_field('job_description_template');

        // Clear the current selection in Job Description Template if designation changes
        frm.set_value('job_description_template', null);
    },

    /*
     * This function triggers when the Job Description Template field is changed.
     * It fetches the Job Description based on the selected Job Description Template.
     */
    job_description_template: function(frm) {
        if (frm.doc.job_description_template) {
            // Fetch Job Description from the selected Job Description Template
            frappe.db.get_value('Job Description Template',{'name': frm.doc.job_description_template},'description',
                function(r) {
                    if (r && r.description) {
                        frm.set_value('description', r.description);
                    }
                }
            );
        }
    }
});
