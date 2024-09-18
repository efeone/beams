frappe.ui.form.on('Voucher Entry', {
    bureau: function(frm) {
      // Triggered when the 'bureau' field is updated
        if (frm.doc.bureau) {
            frappe.db.get_value('Bureau', frm.doc.bureau, ['cost_center', 'company'], function(r) {
                if (r) {
                    frm.set_value('cost_center', r.cost_center);
                    frm.set_value('company', r.company);
                }
            });
        }
    }
});
