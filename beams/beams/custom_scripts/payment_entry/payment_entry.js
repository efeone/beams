frappe.ui.form.on('Payment Entry', {
    payment_type(frm) {
        if (frm.doc.payment_type === 'Pay') {
            frm.set_value('party_type', 'Employee');
        }
    },
    onload_post_render(frm) {
        if (frm.is_new() && frm.doc.payment_type === 'Pay') {
            frm.set_value('party_type', 'Employee');
        }
    },
    party_type(frm) {
        if (frm.doc.party_type === "Employee") {
            frappe.db.get_list('Employee', {
                filters: { user_id: frappe.session.user },
                fields: ['name']
            }).then(records => {
                if (records.length > 0) {
                    frm.set_value("party", records[0].name);
                } else {
                    frappe.msgprint(__("No Employee record found for the current user."));
                }
            });
        }
    }
});
