// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bureau", {
	setup(frm) {
		set_filters(frm);
	},
	regional_bureau(frm) {
		set_regional_bureau_head(frm);
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

/**
 * Fetches and sets the Regional Bureau Head based on the selected Regional Bureau.
 */
function set_regional_bureau_head(frm) {
	if (frm.doc.regional_bureau) {
			frappe.db.get_value(
				'Bureau',
				frm.doc.regional_bureau,
				'regional_bureau_head',
				(r) => {
					if (r && r.regional_bureau_head) {
						frm.set_value('regional_bureau_head', r.regional_bureau_head);
					}
				}
			);
	}
}

