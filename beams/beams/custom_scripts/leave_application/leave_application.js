frappe.ui.form.on('Leave Application', {
    leave_type: function(frm) {
        if (frm.doc.leave_type === "Casual Leave") {
            validate_from_date(frm);
        }
    },

    from_date: function(frm) {
        if (frm.doc.leave_type === "Casual Leave") {
            validate_from_date(frm);
        }
    }
});

function validate_from_date(frm) {
    if (!frm.doc.from_date || !frm.doc.leave_type) {
        return; 
    }

    frappe.call({
        method: 'beams.beams.custom_scripts.leave_application.leave_application.validate_casual_leave_application',
        args: {
            from_date: frm.doc.from_date,
            leave_type: frm.doc.leave_type
        },
        callback: function(response) {
            if (response.exc) {
                frm.set_value('from_date', '');
                frappe.msgprint({
                    title: __('Validation Error'),
                    indicator: 'red',
                    message: __('The From Date is invalid for the selected Leave Type.')
                });
            }
        }
    });
}
