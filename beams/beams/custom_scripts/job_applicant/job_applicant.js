frappe.ui.form.on('Job Applicant', {
    refresh: function (frm) {
        handle_custom_buttons(frm);
        frm.toggle_display('applicant_interview_round', !frm.is_new());
        // Add the "Set Status" group button with "Selected" option only if status is "Local Enquiry Approved"
        if (frm.doc.status === 'Local Enquiry Approved') {
            frm.add_custom_button(__('Selected'), function() {
                frm.set_value('status', 'Selected');
                frm.save();
            }, __('Set Status'));
        }
    },
    status: function(frm) {
        frm.trigger('refresh');
    }
});

function handle_custom_buttons(frm) {
    if (!frm.is_new()) {
      frappe.call({
             method: "beams.beams.custom_scripts.job_applicant.job_applicant.get_existing_local_enquiry_report",
             args: {
                 doc_name: frm.doc.name
             },
             callback: function(r) {
                 if (r.message === "no_report") {
               // Case 1: No report exists; show the "Create" button to create a new report
               frm.add_custom_button(__(' Local Enquiry Report'), function() {
                   // Automatically create the Local Enquiry Report
                   frappe.call({
                   method: "beams.beams.custom_scripts.job_applicant.job_applicant.create_and_return_report",
                   args: {
                       job_applicant: frm.doc.name
                   },
                   callback: function(r) {
                       if (r.message) {
                           frm.add_custom_button(__(' Local Enquiry Report'), function() {
                               frappe.set_route('Form', 'Local Enquiry Report', r.message);
                           }, __('View'));
                       }
                   }
               });

               }, __('Create'));
                 } else if (r.message) {
               // Case 2: Report exists, get the report document
               frappe.db.get_doc("Local Enquiry Report", r.message).then(report => {
                   // Add a button to view the report, regardless of its docstatus
                   frm.add_custom_button(__('Local Enquiry Report'), function() {
                 frappe.set_route('Form', 'Local Enquiry Report', report.name);
                   }, __('View'));
               });
            }
          }
      });
        // Button for Sending Magic Link
        frm.add_custom_button(__('Send Magic Link'), function () {
            frappe.confirm(
                'Are you sure you want to send the magic link to the candidate?',
                function () {
                    frappe.call({
                        method: "beams.beams.custom_scripts.job_applicant.job_applicant.send_magic_link",
                        args: {
                            applicant_id: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint("Magic link has been sent to the candidate.");
                            }
                        }
                    });
                }
            );
        });
    }
}

frappe.ui.form.on('Applicant Interview Round', {
    create_interview: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Check if the form is dirty
        if (frm.is_dirty()) {
            frappe.msgprint(__('Please save your changes before creating or viewing an interview.'));
            return;
        }
        frappe.db.get_value('Interview', {
            job_applicant: frm.doc.name,
            interview_round: row.interview_round
        }, 'name').then((r) => {
            if (r && r.message && r.message.name) {
                frappe.set_route('Form', 'Interview', r.message.name);
            } else {
                // If no Interview exists, open a new unsaved Interview form with pre-filled values
                frappe.model.with_doctype('Interview', function() {
                    let new_interview = frappe.model.get_new_doc('Interview');
                    new_interview.job_applicant = frm.doc.name;
                    new_interview.job_title = frm.doc.job_opening;
                    new_interview.interview_round = row.interview_round;
                    new_interview.scheduled_on = frappe.datetime.now_date();
                    new_interview.status = 'Pending';

                    frappe.set_route('Form', 'Interview', new_interview.name);
                });
            }
        });
    }
});
