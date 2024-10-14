
frappe.ui.form.on('Job Requisition', {
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
    },

    /*
     * This function triggers when the Job Description Template field is changed.
     * It fetches the employee who's status is Left
     */

    refresh: function(frm) {
         frm.set_query('employee_left', function() {
             return {
                 filters: {
                     status: 'Left'
                 }
             };
         });
         /*
          * Sets a filter on the Job Description Template field based on the Designation .
          * Clears the Job Description Template field when the form is refreshed,
          */
         frm.set_query('job_description_template', function() {
             return {
                 filters: {
                     'designation': frm.doc.designation
                 }
             };
         });
    },
    onload: function(frm) {
      if (!frm.doc.requested_by) {
        // Fetch the Employee linked to the current User
        frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        .then(r => {
          if (r && r.message) {
            frm.set_value('requested_by', r.message.name);
          }
        });
      }
    }
});
