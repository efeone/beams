// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt


frappe.ui.form.on("Courier Log", {
    onload(frm) {
        set_employee_name(frm);
    },
    refresh(frm) {
        if (frm.is_new()) return;

        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Employee",
                filters: { user_id: frappe.session.user },
                fieldname: "name"
            },
            callback: function(r) {
                if (!r.message) return;

                const emp_id = r.message.name;

                let recipient_row = frm.doc.recipients?.find(row => row.recepient === emp_id);

                if (frappe.user.has_role("Administrator")) {
                    return;
                }

                if (recipient_row) {
                    if (recipient_row.received && !recipient_row.delivered) {
                        let btn = frm.add_custom_button(__('Received'), function() {
                            recipient_row.delivered = 1;

                            frm.dirty();
                            frm.refresh_field("recipients");

                            frm.save().then(() => {
                                frappe.show_alert({
                                    message: __("You have marked this courier as received."),
                                    indicator: "green"
                                });
                            });
                        });

                        btn.css({
                            'color': 'white',
                            'background-color': '#0d6777ff',
                            'font-weight': 'bold'
                        });

                        if (frm.doc.owner !== frappe.session.user) {
                            frm.set_read_only();
                        }
                    }
                }
            }
        });
    }
});


/**
 * Set the 'handled_by' field to the employee name of the current user.
 */

function set_employee_name(frm) {
    if (!frm.doc.handled_by) {
        frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
            .then(r => {
                if (r.message) frm.set_value('handled_by', r.message.employee_name);
            });
    }
}
