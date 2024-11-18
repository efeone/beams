frappe.ui.form.on('Event', {
  /**
   * Adds a custom button 'Training Request' for users with 'HOD' role
   * This button creates a new 'Training Request' document.
   */
    refresh: function(frm) {
        if (!frm.is_new() && frappe.user.has_role('HOD')) { // Adds the custom button 'Training Request' in the 'Create' section
            frm.add_custom_button('Training Request', function() {
                // Call the server-side function to fetch the employee ID for the current user
                frappe.call({
                    method: "beams.beams.custom_scripts.employee.employee.get_employee_name_for_user",
                    args: {
                        user_id: frappe.session.user
                    },
                    callback: function(response) {
                      if (response.message) {
                          const session_employee = response.message;

                          if (frm.doc.event_participants && frm.doc.event_participants.length > 0) {
                              const other_employees = frm.doc.event_participants.filter(participant => {
                                  const participant_employee = participant.reference_docname;
                                  return participant_employee !== session_employee;
                              });

                              if (other_employees.length > 0) {
                                  const next_employee = other_employees[0].reference_docname;

                                  // Create a new Training Request with the next employee
                                  frappe.new_doc('Training Request', {
                                      employee: next_employee,
                                      training_requested_by: session_employee
                                  });
                              } else {
                                  frappe.msgprint(__('No other employees found in the event participants.'));
                              }
                          } else {
                              frappe.msgprint(__('No participants found in this Event.'));
                          }
                      } else {
                            // Show a message if no employee record is found for the user
                            frappe.msgprint(__('No employee record found for the current user.'));
                        }
                    }
                });
            }, 'Create');
        }
    }
});
