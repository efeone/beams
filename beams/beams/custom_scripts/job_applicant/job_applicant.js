frappe.ui.form.on('Job Applicant', {
    refresh: function (frm) {
        handle_custom_buttons(frm);
        frm.toggle_display('applicant_interview_round', !frm.is_new());
    }
});

function handle_custom_buttons(frm) {
    if (!frm.is_new()) {
        // Button to create Local Enquiry Report
        frm.add_custom_button(frappe._('Local Enquiry Report'), function () {
            frappe.call({
                method: "beams.beams.custom_scripts.job_applicant.job_applicant.create_local_enquiry",
                args: {
                    doc_name: frm.doc.name  // Pass the name of the Job Applicant to the method
                },
                callback: function (r) {
                    if (r.message) {
                        // Redirect to the Local Enquiry Report form
                        frappe.set_route('Form', 'Local Enquiry Report', r.message);
                    }
                },
            });
        }, frappe._('Create'));

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