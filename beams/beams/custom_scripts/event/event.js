frappe.ui.form.on('Event', {
    /**
     * Adds a custom button 'Training Request' for users with 'HOD' role
     * This button creates a new 'Training Request' document.
     */
    refresh: function (frm) {
        // Add filter for 'meeting_room' field
        frm.set_query('meeting_room', function () {
            if (frm.doc.assign_service_unit) {
                return {
                    filters: {
                        allow_appointment: 1
                    }
                };
            }
        });

        if (!frm.is_new() && frappe.user.has_role('HOD')) {
            // Adds the custom button 'Training Request' in the 'Create' section
            frm.add_custom_button('Training Request', function () {
                // Call the server-side function to fetch the employee ID for the current user
                frappe.call({
                    method: "beams.beams.custom_scripts.employee.employee.get_employee_name_for_user",
                    args: {
                        user_id: frappe.session.user
                    },
                    callback: function (response) {
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

        // Add button to create Guest Appointment in the 'Create' group
        frm.add_custom_button(__('Guest Appointment'), () => {
            if (!frm.doc.external_participants || frm.doc.external_participants.length === 0) {
                frappe.msgprint(__('No external participants found to create appointments.'));
                return;
            }

            // Map external participants and open the Guest Appointment DocType
            frappe.new_doc('Guest Appointment', {
                event: frm.doc.name, // Map the current Event to the Guest Appointment
                participants: frm.doc.external_participants.map(participant => ({
                    participant_name: participant.participant_name
                }))
            });
        }, 'Create'); // Add the button under the 'Create' group

        if (frm.doc.meeting_room && frm.doc.starts_on && frm.doc.ends_on) {
            // Check for conflicting events with the selected meeting room and date range
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Event",
                    filters: {
                        meeting_room: frm.doc.meeting_room,
                        // Check if any existing event starts before this event ends and ends after this event starts
                        starts_on: ["<=", frm.doc.ends_on],
                        ends_on: [">=", frm.doc.starts_on],
                        name: ["!=", frm.doc.name] // Exclude the current event
                    },
                    fields: ["name", "starts_on", "ends_on"]
                },
                callback: function (response) {
                    if (response.message && response.message.length > 0) {
                        frm.dashboard.clear_headline()
                        frm.dashboard.set_headline(`The selected Meeting Room <b>${frm.doc.meeting_room}</b> is already assigned to another Event during this time.`, 'red')
                    }
                }
            });
        }
    }
});
