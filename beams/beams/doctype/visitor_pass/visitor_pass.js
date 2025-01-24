// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visitor Pass", {
  issued_date: function (frm) {
      frm.call("validate_issued_date_and_expire_on");
      frm.call("validate_issued_date_and_returned_date");

  },
  expire_on: function (frm) {
      frm.call("validate_issued_date_and_expire_on");
  },
  returned_date:function(frm){
    frm.call("validate_issued_date_and_returned_date");

  }

	// refresh(frm) {
  //
	// },
});
