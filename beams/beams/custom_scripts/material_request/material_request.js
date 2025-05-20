
frappe.ui.form.on('Material Request', {
    onload(frm) {
        if (!frm.doc.requested_by) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    if (r.message) {
                        frm.set_value('requested_by', r.message.name);
                    }
                });
        }
    }
});

