
frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {  
            frm.add_custom_button(__('Sales Invoice'), function() {
                frappe.model.open_mapped_doc({
                    method: "beams.beams.custom_scripts.quotation.quotation.make_sales_invoice",
                    frm: frm
                });
            }, __('Create'));
        }
    }
});
