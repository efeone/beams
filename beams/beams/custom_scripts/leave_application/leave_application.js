frappe.ui.form.on('Leave Application', {
    leave_type: function(frm) {
        if (frm.doc.leave_type === "Casual Leave") {
            validate_from_date(frm);
        }
        if (frm.doc.leave_type) {
            frappe.db.get_value('Leave Type', frm.doc.leave_type, 'is_sick_leave', function(value) {
                if (value.is_sick_leave && frm.doc.from_date && frm.doc.to_date) {
                    var duration = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1;
                    frm.set_df_property('medical_certificate', 'hidden', duration <= 2);
                } else {
                    frm.set_df_property('medical_certificate', 'hidden', true);
                }
                frm.refresh_field('medical_certificate');
            });
        } else {
            frm.set_df_property('medical_certificate', 'hidden', true);
            frm.refresh_field('medical_certificate');
        }
    },

    from_date: function(frm) {
        if (frm.doc.leave_type === "Casual Leave") {
            validate_from_date(frm);
        }
        frm.trigger('leave_type');
    },
    to_date: function(frm) {
        frm.trigger('leave_type');
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
