// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Appraisal Consent", {
	refresh(frm) {
		if (frm.is_new()) {
	  fetch_terms_from_settings(frm);
	}
	render_appraisal_terms(frm);
  },
  terms_and_conditions(frm) {
	render_appraisal_terms(frm);
  }
});


/**
 * Fetch default Appraisal Terms from Beams HR Settings
 */
function fetch_terms_from_settings(frm) {
  frappe.db.get_value("Beams HR Settings", {}, "appraisal_consent_terms")
	.then(r => {
	  if (r.message && r.message.appraisal_consent_terms) {
		frappe.db.get_value("Terms and Conditions", r.message.appraisal_consent_terms, "terms")
		  .then(res => {
			if (res.message && res.message.terms) {
			  frm.set_value("terms_and_conditions", res.message.terms);
			  render_appraisal_terms(frm);
			}
		  });
	  }
	});
}


/**
 * Show appraisal terms in a scrollable box
 * and enable consent checkbox after reading.
 */
function render_appraisal_terms(frm) {
  $("#appraisal-terms-container").remove();

  if (frm.doc.terms_and_conditions) {
	const terms_content = frm.doc.terms_and_conditions || "No Terms available.";

	const container = $("<div>")
	  .attr("id", "appraisal-terms-container")
	  .css({
		maxHeight: "300px",       
		overflowY: "auto",        
		border: "1px solid #ccc",
		padding: "10px",
		marginBottom: "20px",
		backgroundColor: "#fafafa",
		whiteSpace: "pre-wrap"
	  })
	  .html(terms_content);
	frm.set_df_property("terms_and_conditions", "hidden", 1);
	$(frm.fields_dict.consent_given.wrapper).before(container);
	frm.set_df_property("consent_given", "read_only", 1);
	setTimeout(() => {
	  if (container[0].scrollHeight > container.innerHeight()) {
		container.on("scroll", function () {
		  if (
			container.scrollTop() + container.innerHeight() >=
			container[0].scrollHeight
		  ) {
			frm.set_df_property("consent_given", "read_only", 0);
		  }
		});
	  } else {
		frm.set_df_property("consent_given", "read_only", 0);
	  }
	}, 300);
  } else {
	frm.set_df_property("consent_given", "read_only", 1);
  }
}