frappe.ui.form.on('Job Applicant', {
    refresh: function (frm) {
        handle_custom_buttons(frm);
        frm.toggle_display('applicant_interview_rounds', !frm.is_new());
    },
    status: function (frm) {
        frm.trigger('refresh');
    },
    willing_to_work_on_location: function (frm) {
        if (frm.doc.willing_to_work_on_location) {
            if (frm.doc.job_title) {
                frappe.call({
                    method: 'beams.beams.custom_scripts.job_applicant.job_applicant.get_job_opening_location',
                    args: {
                        'job_opening': frm.doc.job_title
                    },
                    callback: function (r) {
                        if (r.message) {
                            frm.set_value('location', r.message);
                        } else {
                            frm.set_value('location', '');
                        }
                    }
                });
            }
        } else {
            // Clear location if checkbox is unchecked
            frm.set_value('location', '');
        }
    }
});

function handle_custom_buttons(frm) {
    if (!frm.is_new()) {
        if (frappe.user_roles.includes('HR Manager')) {
            // Handle "Appointment Letter" button for "Training Completed" status
            if (frm.doc.status === 'Training Completed') {
                frappe.db.get_value('Appointment Letter', { 'job_applicant': frm.doc.name }, 'name', function (result) {
                    if (!result || !result.name) {
                        frm.add_custom_button(__('Appointment Letter'), function () {
                            frappe.new_doc('Appointment Letter', {
                                job_applicant: frm.doc.name
                            });
                        }, __('Create'));
                    }
                });
                // Remove the "Interview" button when status is "Training Completed"
                frm.remove_custom_button(__('Interview'), __('Create'));
            }

            // Handle "Job Proposal" button for "Selected" status
            if (frm.doc.status === 'Selected') {
                frappe.db.get_value('Job Proposal', { 'job_applicant': frm.doc.name }, 'name', function (result) {
                    if (!result || !result.name) {
                        frm.add_custom_button(__('Job Proposal'), function () {
                            frappe.new_doc('Job Proposal', {
                                job_applicant: frm.doc.name
                            });
                        }, __('Create'));
                    } else {
                        frm.remove_custom_button(__('Job Proposal'), __('Create'));
                    }
                });
            }

            frappe.call({
                method: 'beams.beams.custom_scripts.job_applicant.job_applicant.get_existing_local_enquiry_report',
                args: {
                    doc_name: frm.doc.name
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.db.get_doc('Local Enquiry Report', response.message).then(report => {
                            frm.add_custom_button(__('Local Enquiry Report'), function () {
                                frappe.set_route('Form', 'Local Enquiry Report', report.name);
                            }, __('View'));
                        });
                    } else {
                        frm.add_custom_button(__('Local Enquiry Report'), function () {
                            frappe.call({
                                method: 'beams.beams.custom_scripts.job_applicant.job_applicant.create_and_return_report',
                                args: {
                                    job_applicant: frm.doc.name
                                },
                                callback: function (createResponse) {
                                    if (createResponse.message) {
                                        frm.add_custom_button(__('Local Enquiry Report'), function () {
                                            frappe.set_route('Form', 'Local Enquiry Report', createResponse.message);
                                        }, __('View'));
                                        frm.refresh();
                                    }
                                }
                            });
                        }, __('Create'));
                    }
                }
            });

            if (!frm.doc.is_form_submitted) {
                // Button for Sending Magic Link
                frm.add_custom_button(__('Send Magic Link'), function () {
                    frappe.confirm('Are you sure you want to send the magic link to the candidate?', function () {
                        frappe.call({
                            method: 'beams.beams.custom_scripts.job_applicant.job_applicant.send_magic_link',
                            args: {
                                applicant_id: frm.doc.name
                            },
                            callback: function (r) {
                                if (r.message) {
                                    frm.reload_doc();
                                }
                            }
                        });
                    });
                });
            }

            if (frm.doc.status === 'Accepted') {
                frm.add_custom_button(__('Training Completed'), function () {
                    frm.set_value('status', 'Training Completed');
                    frm.save();
                }, __('Set Status'));
            }

            if (frm.doc.status !== 'Rejected' && frm.doc.status !== 'Selected') {
                frm.add_custom_button(__('Rejected'), function () {
                    frm.set_value('status', 'Rejected');
                    frm.save();
                }, __('Set Status'));
            }

            // Show "Hold" button only if status is neither "Rejected" nor "Hold"
            if (frm.doc.status !== 'Hold' && frm.doc.status !== 'Rejected' && frm.doc.status !== 'Selected') {
                frm.add_custom_button(__('Hold'), function () {
                    frm.set_value('status', 'Hold');
                    frm.save();
                }, __('Set Status'));
            }

            if (['Hold', 'Local Enquiry Approved'].includes(frm.doc.status)) {
                frm.add_custom_button(__('Selected'), function () {
                    frm.set_value('status', 'Selected');
                    frm.save();
                }, __('Set Status'));
            }

            // Remove "Interview" button if status is "Training Completed", "Job Proposal Created", "Job Proposal Accepted ,"Interview Completed" or "Selected"
            if (['Training Completed', 'Job Proposal Created', 'Job Proposal Accepted', 'Interview Completed', 'Selected'].includes(frm.doc.status)) {
                frm.remove_custom_button(__('Interview'), __('Create'));
            }

            if (frm.doc.status === 'Open') {
                frm.add_custom_button(__('Shortlist'), function () {
                    frm.set_value('status', 'Shortlisted');
                    frm.save();
                }, __('Set Status'));
            }
        }
    }
}

frappe.ui.form.on('Applicant Interview Round', {
    create_interview: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Check if the form is dirty
        if (frm.is_dirty()) {
            frappe.msgprint(__('Please save your changes before creating or viewing an interview.'));
            return;
        }
        // View created Interviews. If no Interview exists, open a new unsaved Interview form with pre-filled values
        if (row.interview_reference) {
            frappe.set_route('Form', 'Interview', row.interview_reference);
        }
        else {
            frappe.model.with_doctype('Interview', function () {
                let new_interview = frappe.model.get_new_doc('Interview');
                new_interview.job_applicant = frm.doc.name;
                new_interview.job_title = frm.doc.job_opening;
                new_interview.interview_round = row.interview_round;
                new_interview.scheduled_on = frappe.datetime.now_date();
                new_interview.status = 'Pending';
                frappe.set_route('Form', 'Interview', new_interview.name);
            });
        }
    }
});

frappe.ui.form.on('Job Applicant', {
    refresh: function(frm) {
        const statuses = [
            'Document Uploaded', 'Open', 'Pending Document Upload', 'Shortlisted',
            'Local Enquiry Approved', 'Selected', 'Local Enquiry Started',
            'Local Enquiry Rejected', 'Local Enquiry Completed'
        ];

        if (statuses.includes(frm.doc.status)) {
          // Remove "Local Enquiry Report" button for the specified statuses
            frm.remove_custom_button(__('Local Enquiry Report'), __('Create'));

            if (frm.doc.status !== 'Document Uploaded') {
          // Additionally remove "Interview" button except for "Document Uploaded" status
                frm.remove_custom_button(__('Interview'), __('Create'));
            }
        }
    }
});
