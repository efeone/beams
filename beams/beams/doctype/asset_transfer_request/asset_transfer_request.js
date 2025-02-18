// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

 frappe.ui.form.on("Asset Transfer Request", {
   posting_date:function (frm){
       frm.call("validate_posting_date");
     },
 });
