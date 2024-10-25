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

        if(frm.doc.status =="Approved") {
          // Create Job Opening Button
          frm.add_custom_button(
              __("Create Job Opening"),
              () => {
                  frappe.model.open_mapped_doc({
                      method: "beams.beams.custom_scripts.job_requisition.job_requisition.make_job_opening",
                      source_name: frm.doc.name,  // Pass the current Job Requisition ID
                  });
              },
              __("Create"),
              "btn-secondary"  // Set as a secondary button
          );

          // Associate Job Opening Button
          frm.add_custom_button(
              __("Associate Job Opening"),
              () => {
                  frappe.prompt(
                      {
                          label: __("Job Opening"),
                          fieldname: "job_opening",
                          fieldtype: "Link",
                          options: "Job Opening",
                          reqd: 1,
                          get_query: () => {
                              const filters = {
                                  company: frm.doc.company,
                                  status: "Open",
                                  designation: frm.doc.designation,
                              };

                              if (frm.doc.department) {
                                  filters.department = frm.doc.department;
                              }

                              return { filters: filters };
                          },
                      },
                      (values) => {
                          frm.call({
                              method: "beams.beams.custom_scripts.job_requisition.job_requisition.associate_job_opening",
                              args: {
                                  job_opening: values.job_opening,
                                  job_requisition: frm.doc.name  // Pass the current Job Requisition ID if needed
                              },
                              callback: function (r) {
                                  if (!r.exc) {
                                      frappe.msgprint(
                                          __("Job Opening associated successfully."),
                                          __("Success")
                                      );
                                      frm.reload_doc(); // Reload the form to reflect changes
                                  }
                              },
                              error: function (err) {
                                  console.error(err);
                                  frappe.msgprint(
                                      __("There was an issue associating the Job Opening."),
                                      __("Error")
                                  );
                              },
                          });
                      },
                      __("Associate Job Opening"),
                      __("Submit")
                  );
              },
              __("Create"),
              "btn-secondary"  // Set as a secondary button
          );
        }



        /*
         * Sets a filter on the Job Description Template field based on the Designation.
         * Clears the Job Description Template field when the form is refreshed.
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

// Rename Actions Button  as 'Create'  not primary action button
     $(document).ready(function () {
          // Find the specific custom "Actions" button dropdown using the parent or group
          var dropdownActions = frm.page.inner_toolbar
              .find('button:contains("Actions")')
              .first();

          // Rename this specific "Actions" button to "Create"
          if (dropdownActions.length) {
              dropdownActions.text("Create");
          }
      });
    },

    /*
     * This script automatically fills the job description in the Job Requisition form based on
     * the selected Job Description Template and the current form details.
     */
    job_description_template: function (frm) {
        if (frm.doc.job_description_template) {
            frappe.call({
                method: "beams.beams.custom_scripts.job_requisition.job_requisition.display_template_content",
                args: {
                    template_name: frm.doc.job_description_template,
                    doc: frm.doc,
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("description", r.message);
                    }
                },
            });
        }
    },
});
