frappe.ui.form.on('Sales Order', {
  // Trigger the function when the 'sales_type' field changes
  sales_type: function(frm) {
      if (frm.doc.sales_type) {
        // Set a custom query filter for the 'item_code' field in the 'items' child table
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
