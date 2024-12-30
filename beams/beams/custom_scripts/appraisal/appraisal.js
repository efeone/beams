// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Appraisal", {
	refresh(frm) {
    if(!frm.doc.__islocal){
      frappe.require("performance_custom.bundle.js", () => {
			const feedback_history = new hrms.PerformanceFeedbackk({
				frm: frm,
				wrapper: $(frm.fields_dict.custom_feedback_html_custom.wrapper),
			});
			feedback_history.refresh();
		});
    }

	},
});
