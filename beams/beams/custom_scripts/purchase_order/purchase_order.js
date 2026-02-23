frappe.ui.form.on('Purchase Order', {
	refresh(frm) {
		workflow_actions(frm);
	},
	is_budgeted: function(frm){
		clear_checkbox_exceed(frm);
	}
});

/**
 * Shows workflow buttons to the Purchase Order form based on the total amount.
 */
function workflow_actions(frm) {
	if (frm.doc.workflow_state === "Pending Accounts Approval"){;
		const add_workflow_button = (label, action) => {
			frm.page.add_action_item(__(label), () => {
				frappe.xcall('frappe.model.workflow.apply_workflow', {
					doc: frm.doc,
					action: action
				})
			});
		};

		frappe.db.get_single_value('Beams Accounts Settings', 'purchase_threshold')
			.then(threshold => {
				if (!threshold) {
					return;
				}

				frm.page.clear_actions_menu();
				const grand_total = frm.doc.grand_total;
				let actions = ['Forward to CEO'];
				if (grand_total < threshold) {
					actions.unshift('Approve', 'Reject');
				}

				actions.forEach(action => add_workflow_button(action, action));
			});
		}

}

/**
* Clears the "is_budget_exceeded" checkbox if "is_budgeted" is unchecked.
*/
function clear_checkbox_exceed(frm){
	if (frm.doc.is_budgeted == 0){
		frm.set_value("is_budget_exceeded", 0);
	}
}
