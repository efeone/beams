frappe.ui.form.on('Expense Claim',{
	refresh(frm){
		clear_checkbox_exceed(frm);
	},
	is_budgeted:function(frm){
		clear_checkbox_exceed(frm);
	},
});

/**
* clear the "is_budget_exceeded" checkbox if "is_budgeted" is unchecked.
*/
function clear_checkbox_exceed(frm){
	if(frm.doc.is_budgeted == 0){
		frm.set_value("is_budget_exceeded", 0);
	}
}
