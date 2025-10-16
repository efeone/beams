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
		handle_custom_buttons (frm);
	},
	job_offer: function (frm) {
		handle_custom_buttons (frm);
	},
	proposed_ctc: function (frm) {
		frm.call("validate_proposed_ctc");
	}
});

/**
 * Adds custom buttons to the Compensation Proposal form based on the document state.
 */
function handle_custom_buttons (frm) {
	if (frm.doc.workflow_state === 'Applicant Accepted' && frm.doc.job_offer) {
		frm.add_custom_button(__('Job Offer'), function () {
			frappe.set_route('Form', 'Job Offer', frm.doc.job_offer);
		}, __('View'));
	}
}
