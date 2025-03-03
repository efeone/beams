// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Incident Record", {
  posting_date:function (frm){
      frm.call("validate_posting_date");
    },
  offense_date_and_time: function (frm) {
      frm.call("validate_offense_date_and_time");
    }
});
