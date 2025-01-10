// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Appraisal Category", {
  validate: function(frm) {
      if (frm.doc.appraisal_threshold < 0 || frm.doc.appraisal_threshold > 5) {
          frappe.throw(__('Appraisal Threshold must be between 0 and 5.'));
      }
  }
});
