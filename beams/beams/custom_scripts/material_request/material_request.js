
frappe.ui.form.on('Material Request', {
	onload(frm) {
		if (!frm.doc.requested_by) {
			frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
				.then(r => {
					if (r.message) {
						frm.set_value('requested_by', r.message.name);
					}
				});
		}
	},
	refresh(frm) {
		clear_checkbox_exceed(frm);
	},
	is_budgeted: function(frm){	
		clear_checkbox_exceed(frm);
	}
});

/**
* Clears the "budget_exceeded" checkbox if "is_budgeted" is unchecked.
*/
function clear_checkbox_exceed(frm){
	if (frm.doc.is_budgeted == 0){
		frm.set_value("budget_exceeded", 0);
	}
}
