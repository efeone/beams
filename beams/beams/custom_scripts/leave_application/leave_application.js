frappe.ui.form.on('Leave Application', {
    leave_type: function(frm) {
        validate_from_date(frm);
        if (frm.doc.leave_type) {
            frappe.db.get_value('Leave Type', frm.doc.leave_type,['is_sick_leave', 'medical_leave_required'], function(value) {
                if (value.is_sick_leave && frm.doc.from_date && frm.doc.to_date) {
                    var duration = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1;
                    if (value.medical_leave_required && duration > value.medical_leave_required) {
                        frm.set_df_property('medical_certificate', 'hidden', false);
                        frm.set_df_property('medical_certificate', 'reqd', true);
                    } else {
                        frm.set_df_property('medical_certificate', 'hidden', false);
                        frm.set_df_property('medical_certificate', 'reqd', false);
                    }
                } else {
                    frm.set_df_property('medical_certificate', 'hidden', true);
                    frm.set_df_property('medical_certificate', 'reqd', false);
                }
                frm.refresh_field('medical_certificate');
            });
        } else {
            frm.set_df_property('medical_certificate', 'hidden', true);
            frm.set_df_property('medical_certificate', 'reqd', false);
            frm.refresh_field('medical_certificate');
        }
    },

    from_date: function(frm) {
        validate_from_date(frm);
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
        method: 'beams.beams.custom_scripts.leave_application.leave_application.validate_leave_advance_days',
        args: {
            from_date: frm.doc.from_date,
            leave_type: frm.doc.leave_type
        },
        callback: function(response) {
            if (response.exc) {
                frm.set_value('from_date', '');
            }
        }
    });
}
