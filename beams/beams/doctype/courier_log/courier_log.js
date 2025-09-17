// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt


frappe.ui.form.on("Courier Log", {
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

                let emp_id = r.message.name;

                let recipient_row = frm.doc.recipients?.find(row => row.recepient === emp_id);

                if (frappe.user.has_role("Administrator")) {
                    return;
                }

                if (recipient_row) {
                    if (recipient_row.delivered) {
                        let btn = frm.add_custom_button(__('Received'), function() {
                            recipient_row.received = 1;

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
