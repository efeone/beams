frappe.ui.form.on("Item", {
    is_service_item: function(frm) {
        if (frm.doc.is_service_item) {
            frm.set_value("is_stock_item", 0);
            frm.clear_table("item_defaults");
            frm.refresh_field("item_defaults");
        }
    }
});
