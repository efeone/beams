// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Security Patrol Log', {
    patrol_template: function (frm) {
        if (frm.doc.patrol_template) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Patrol Log Template',
                    name: frm.doc.patrol_template
                },
                callback: function (r) {
                    if (r.message) {
                        frm.clear_table('patrol_log');
                        (r.message.patrol_log || []).forEach(function (d) {
                            let row = frm.add_child('patrol_log');
                            row.service_unit = d.service_unit;
                            row.remarks = d.remarks;
                        });
                        frm.refresh_field('patrol_log');
                    }
                }
            });
        }
    }
});
