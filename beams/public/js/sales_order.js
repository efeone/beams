frappe.ui.form.on('Sales Order', {
  sales_type: function(frm) {
      if (frm.doc.sales_type) {
        frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
          return {
            filters: {
              'sales_type': frm.doc.sales_type
            }
         };
      };
    }
    frm.clear_table('items');
    frm.refresh_field('items');
  }
});
