// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Local Enquiry Report', {
    setup: function (frm) {
        set_filters(frm);
    },
    before_workflow_action: function (frm) {
        if (frm.selected_workflow_action == 'Enquiry Completed') {
            frm.set_df_property('enquiry_report', 'reqd', 1);
            frm.set_df_property('information_given_by', 'reqd', 1);
            frm.set_df_property('information_given_by_designation', 'reqd', 1);
            if (!frm.doc.enquiry_report.length) {
                frm.scroll_to_field('enquiry_report');
                frappe.dom.unfreeze();
                frappe.throw({ message: __("Please fill the <b>`Enquiry Report`</b> ."), title: __("Missing field") });
            }
            if (!frm.doc.information_given_by) {
                frm.scroll_to_field('information_given_by');
                frappe.dom.unfreeze();
                frappe.throw({ message: __("Please fill the <b>`Person Name`</b> ."), title: __("Missing field") });
            }
            if (!frm.doc.information_given_by_designation) {
                frm.scroll_to_field('information_given_by_designation');
                frappe.dom.unfreeze();
                frappe.throw({ message: __("Please fill the <b>`Designation`</b> ."), title: __("Missing field") });
            }
        }
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