
frappe.ui.form.on('Job Requisition', {
    refresh: function(frm) {
        // Set the query for employee_left based on request_for
        frm.set_query('employee_left', function() {
            if (frm.doc.request_for === 'Employee Exit') {
                return {
                    filters: {
                        status: 'Left'  // Assuming 'status' is the field that indicates the employee's status
                    }
                };
            } else {
                return {
                    filters: {
                        // No filter if it's not Employee Exit
                    }
                };
            }
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

    request_for: function(frm) {
        // When request_for changes, reset the employee_left field
        frm.set_value('employee_left', []);
        frm.refresh_field('employee_left');  // Refresh the field to apply the new query
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
