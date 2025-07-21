// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Checkin Permission", {
	onload(frm) {
        if (!frm.is_new()|| frm.doc.employee) return;
        if(frappe.session.user !== "Administrator"){
            frappe.call({
                method:'beams.beams.doctype.employee_checkin_permission.employee_checkin_permission.get_employee_for_current_user',
                callback: function(r){
                    if(r.message){
                        frm.set_value('employee',r.message);
                    }else {
                        frappe.msgprint(__('No Employee record linked to this user.'));
                    }
                }
            });
        }
	},
    employee: function(frm){
        set_shift_based_on_assignment(frm);
    },
    date: function(frm){
        set_shift_based_on_assignment(frm);
    }
});

function set_shift_based_on_assignment(frm) {
    /**
    * Sets the shift field on the form based on the employee and date by fetching the assigned shift using a server-side method.
    */
    if (frm.doc.employee && frm.doc.date) {
        frappe.call({
            method: 'beams.beams.doctype.employee_checkin_permission.employee_checkin_permission.get_shift_for_employee_on_date',
            args: {
                employee: frm.doc.employee,
                date: frm.doc.date
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value('shift', r.message);
                }           
            }
        });
    }
}