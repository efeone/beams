frappe.ui.form.on('Employee Onboarding', {
  refresh: function(frm) {
      // Make a server call to check if a CPAL already exists for the employee
      frappe.call({
          method: 'frappe.client.get_list',
          args: {
              doctype: 'Company Policy Acceptance Log',
              filters: {
                  'employee': frm.doc.employee
              },
              fields: ['name'],
          },
          callback: function(response) {
              if (response.message && response.message.length > 0) {
                  // If CPAL document exists, show the 'View CPAL' button
                  frm.remove_custom_button(__('Company Policy Acceptance Log'));
                  frm.add_custom_button(__('Company Policy Acceptance Log'), function () {
                      frappe.set_route('Form', 'Company Policy Acceptance Log', response.message[0].name);
                  }, __('View'));
              } else {
                  // If no CPAL exists, show the 'Create CPAL' button
                  frm.add_custom_button(__('Company Policy Acceptance Log'), function () {
                      frappe.call({
                          method: "beams.beams.custom_scripts.employee_onboarding.employee_onboarding.create_cpal",
                          args: {
                              source_name: frm.doc.name
                          },
                          callback: function(response) {
                              if (response.message) {
                                  // Route to CPAL document form
                                  frappe.set_route('Form', 'Company Policy Acceptance Log', response.message);
                              }
                          },
                      });
                  }, __('Create'));
              }
          },
      });

      // Check if the Activities child table exists
      if (frm.fields_dict['activities']) {
          // Hide the 'Required for Employee Creation' field in the grid
          frm.fields_dict['activities'].grid.toggle_display('required_for_employee_creation', false);
      }
      frm.set_df_property('job_offer', 'read_only', 1);

  },

  employee: function(frm) {
      // If employee is selected, fetch employee details
      if (frm.doc.employee) {
          frappe.call({
              method: 'frappe.client.get',
              args: {
                  doctype: 'Employee',
                  name: frm.doc.employee
              },
              callback: function(response) {
                  if (response.message) {
                      let employee = response.message;
                      // Set the fetched values in the Employee Onboarding form
                      frm.set_value('department', employee.department);
                      frm.set_value('designation', employee.designation);
                      frm.set_value('date_of_joining', employee.date_of_joining);
                      frm.set_value('holiday_list', employee.holiday_list);
                      frm.set_value('employee_grade', employee.grade);
                      frm.refresh_fields();
                  } else {
                      frappe.msgprint(__('No employee details found.'));
                  }
              },
          });
      }
  },

  job_applicant: function(frm) {
      if (frm.doc.job_applicant) {
          frappe.call({
              method: 'frappe.client.get',
              args: {
                  doctype: 'Job Offer',
                  filters: { 'job_applicant': frm.doc.job_applicant }, // Fetch job offer based on job applicant
                  fields: ['name']
              },
              callback: function(response) {
                  if (response.message) {
                      frm.set_value('job_offer', response.message.name);
                      frm.set_df_property('job_offer', 'read_only', 1);
                      frm.refresh_fields();
                  } else {
                      frappe.msgprint(__('No job offer found for the selected applicant.'));
                  }
              },
          });
      }
  }
});
