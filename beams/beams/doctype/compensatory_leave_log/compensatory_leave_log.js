frappe.ui.form.on('Compensatory Leave Log', {
    end_date: function(frm) {
        if (frm.doc.start_date && frm.doc.end_date) {
            if (frm.doc.end_date < frm.doc.start_date) {
                frappe.msgprint(__('End Date cannot be before Start Date'));
                frm.set_value('end_date', '');
            }
        }
    }
});
