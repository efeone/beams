// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Night Patrol Log', {
    start_time: function(frm) {
        validate_patrol_time(frm);
    },
    end_time: function(frm) {
        validate_patrol_time(frm);
    }
});

function validate_patrol_time(frm) {
    const start = frm.doc.start_time;
    const end = frm.doc.end_time;

    if (start && end && start >= end) {
        frappe.msgprint(__('Start Time must be earlier than End Time.'));
        frm.set_value('end_time', null); 
    }
}
