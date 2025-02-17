// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Bundle", {
	refresh:function(frm) {
    frm.fields_dict['stock_items'].grid.get_field('item').get_query = function(doc, cdt, cdn) {
      return {
          filters: {
              is_fixed_asset: 0
          }
      };
  };
},
validate: function(frm) {
    if (!frm.doc.asset_bundle_stock_items?.length && !frm.doc.assets?.length && !frm.doc.bundles?.length) {
        frappe.msgprint(__('At least one of Stock Items, Assets, or Bundles must be filled in.'));
        frappe.validated = false;
    }
}
});
