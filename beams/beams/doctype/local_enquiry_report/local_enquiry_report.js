// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Local Enquiry Report", {
	onload(frm) {
        frm.set_value('information_collected_by', frappe.session.user);

	},
});
