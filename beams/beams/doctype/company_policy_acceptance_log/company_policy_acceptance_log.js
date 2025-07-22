// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company Policy Acceptance Log', {
	onload: function (frm) {
		if (frappe.session.user !== 'Administrator') {
			frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
				.then(r => {
					if (r.message && r.message.name) {
						const employee_id = r.message.name;
						frm.set_value('employee', employee_id);

						// Wait for fields to render, then make them editable
						frappe.after_ajax(() => {
							frm.set_df_property('read_and_accepted', 'read_only', false);
							frm.set_df_property('digital_sign', 'read_only', false);
						});
					} else {
						// No linked employee: keep fields read-only
						frm.set_df_property('read_and_accepted', 'read_only', true);
						frm.set_df_property('digital_sign', 'read_only', true);
					}
				});
		} else {
			// Administrator: read-only fields
			frm.set_df_property('read_and_accepted', 'read_only', true);
			frm.set_df_property('digital_sign', 'read_only', true);
		}
	}
});
