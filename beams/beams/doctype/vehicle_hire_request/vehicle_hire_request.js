// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Hire Request", {
	refresh(frm) {
    frm.add_custom_button(__('Purchase Invoice'), function (){

    }, __("Create"));

	},
	posting_date:function (frm){
	frm.call("validate_posting_date");
}
});
