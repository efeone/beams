frappe.ui.form.on('Opportunity', {
    refresh: function(frm) {
        setTimeout(() => {
            frm.remove_custom_button('Supplier Quotation', 'Create');
            frm.remove_custom_button('Request For Quotation', 'Create');
            frm.remove_custom_button('Release Order', 'Create');
        }, 500);
    }
});
