// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Local Enquiry Report', {
    setup: function (frm) {
        set_filters(frm);
    },
    refresh: function (frm) {
        handle_field_properties(frm)
    }
});

function set_filters(frm) {
    frm.set_query('enquiry_officer', () => {
        return {
            query: 'beams.beams.doctype.local_enquiry_report.local_enquiry_report.enquiry_officer_query'
        };
    });

    frm.set_query('job_applicant', () => {
        return {
            filters: {
                'status': 'Shortlisted from Interview'
            }
        };
    });
}

function handle_field_properties(frm) {
    frm.set_df_property('information_collected_by_section', 'hidden', 1)
    if (frm.doc.workflow_state == 'Draft') {
        frm.set_df_property('enquiry_officer', 'hidden', 1)
        frm.set_df_property('enquiry_details', 'hidden', 1)
    }

    if (frm.doc.workflow_state == 'Assigned to Admin') {
        frm.set_df_property('enquiry_officer', 'hidden', 0)
        frm.set_df_property('enquiry_details', 'hidden', 1)
    }

    if (['Enquiry on Progress', 'Pending Approval', 'Approved', 'Rejected'].includes(frm.doc.workflow_state)) {
        frm.set_df_property('information_collected_by_section', 'hidden', 0)
    }
}