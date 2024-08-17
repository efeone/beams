frappe.ui.form.on('Account', {
    validate: function (frm) {
        if (frm.doc.__islocal) {
            frm.set_value('disabled', 1);
        } else {
            if (frm.doc.workflow_state === 'Approved') {
                frm.set_value('disabled', 0);
            } else {
                frm.set_value('disabled', 1); 
            }
        }
    }
});
