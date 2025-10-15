frappe.ui.form.on("Employment Type", {
	refresh(frm) {
		set_default_leave_policy(frm);
	},
});

/**
 * Filter `default_leave_policy` to only show submitted Leave Policies
 * in Employment Type.
 */
function set_default_leave_policy(frm) {
	frm.fields_dict.default_leave_policy.get_query = function() {
		return {
			filters: {
				"docstatus": 1
			}
		};
	};
}