// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Appraisal Consent", {
	refresh(frm) {
		render_appraisal_consent_terms(frm);
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			add_view_appraisal_button(frm);
		}
	}
});

/**
 * Render appraisal consent Terms & Conditions in the form.
 * - Reads linked Terms & Conditions from HR Settings (singleton).
 * - Fetches its `terms` content and displays it in a styled box.
 * - Toggles the "consent_given" checkbox based on availability.
 *
 * @param {frappe.ui.Form} frm - Current Employee Appraisal Consent form.
 */
function render_appraisal_consent_terms(frm) {
	// Always clear before re-render
	$(frm.fields_dict['terms_and_conditions'].wrapper).empty();
	frappe.db.get_single_value("Beams HR Settings", "appraisal_consent_terms")
		.then(terms_name => {
			if (terms_name) {
				frappe.db.get_value("Terms and Conditions", terms_name, "terms")
					.then(res => {
						let terms_text = res?.message?.terms;
						if (terms_text) {
							// Render formatted Terms text inside styled scrollable box
							$(frm.fields_dict['terms_and_conditions'].wrapper).html(`
								<div class="alert alert-info"
									 style="max-height: 250px; overflow-y: auto; padding: 10px; border-radius: 6px;">
									${terms_text}
								</div>
							`);
							toggle_consent_checkbox_readonly(frm, false);
						} else {
							// No terms text found → clear + disable checkbox
							$(frm.fields_dict['terms_and_conditions'].wrapper).empty();
							toggle_consent_checkbox_readonly(frm, true);
						}
					});
			} else {
				// No Terms & Conditions linked in HR Settings → clear + disable checkbox
				$(frm.fields_dict['terms_and_conditions'].wrapper).empty();
				toggle_consent_checkbox_readonly(frm, true);
			}
		})
		.catch(err => {
			console.error("Error fetching appraisal consent terms:", err);
			toggle_consent_checkbox_readonly(frm, true);
		});
}

/**
 * Enable or disable the "consent_given" checkbox dynamically.
 *
 * @param {frappe.ui.Form} frm - Current form.
 * @param {boolean} readonly - If true, disable the checkbox.
 */
function toggle_consent_checkbox_readonly(frm, readonly) {
	const fieldname = "consent_given";

	if (!frm.fields_dict[fieldname]) return;
	frm.set_df_property(fieldname, "read_only", readonly);
	const input = frm.fields_dict[fieldname].$wrapper.find("input[type=checkbox]");
	if (input.length) {
		input.prop("disabled", readonly);
	}
}

/**
 * Add a "View Appraisal" button to navigate to the linked Appraisal document.
 *
 * @param {frappe.ui.Form} frm - The current form.
 */
function add_view_appraisal_button(frm) {
	if (frm.doc.appraisal) {
		frm.add_custom_button(__("View Appraisal"), () => {
			frappe.set_route("Form", "Appraisal", frm.doc.appraisal);
		});
	}
}