frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {
            // Show the Sales Invoice button
            frm.add_custom_button(__('Sales Invoice'), function() {
                frappe.model.open_mapped_doc({
                    method: "beams.beams.custom_scripts.quotation.quotation.make_sales_invoice",
                    frm: frm
                });
            }, __('Create'));

            // Show the Purchase Invoice button only if is_barter is checked
            if (frm.doc.is_barter) {
                frm.add_custom_button(__('Purchase Invoice'), function() {
                    frappe.model.open_mapped_doc({
                        method: "beams.beams.custom_scripts.quotation.quotation.make_purchase_invoice",
                        frm: frm
                    });
                }, __('Create'));
            }
        }
    }
});
