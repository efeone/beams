// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Compensation Proposal', {
    refresh: function(frm) {
        frm.set_query('job_applicant', function() {
            return {
                filters: {
                    status: 'Selected'
                }
            };
        });
    },
    proposed_ctc: function (frm) {
        frm.call("validate_proposed_ctc");
    }
});
