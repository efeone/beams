// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bureau", {
	setup(frm) {
		set_filters(frm);
	}
});

/*
Show Bureaus marked as "Is Parent Bureau = 1" appear in the selection list.
*/
let set_filters = function (frm) {
	frm.set_query("regional_bureau", function() {
		return {
			filters: {
				is_parent_bureau: 1
			}
		}
	});
}
