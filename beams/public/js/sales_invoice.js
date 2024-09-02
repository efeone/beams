frappe.ui.form.on('Sales Invoice', {
  refresh: function(frm) {
    frm.set_query('actual_customer', function() {
      return {
        filters: {
          'is_agent': 0
        }
      };
    });
  },
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
    check_include_in_ibf(frm);
    frm.clear_table('items');
    frm.refresh_field('items');
  },
  is_barter_invoice: function(frm) {
    check_include_in_ibf(frm);
  },
  is_agent: function(frm) {
    check_include_in_ibf(frm);
  },
  onload: function(frm) {
    if (frm.is_new) {
      check_include_in_ibf(frm);
    }
  },

});

let check_include_in_ibf = function(frm) {
  frappe.db.get_value('Sales Type', frm.doc.sales_type, 'is_time_sales', function(value) {
    if (value && value.is_time_sales && !frm.doc.is_barter_invoice && frm.doc.is_agent) {
      frm.set_value('include_in_ibf', 1);
    } else {
      frm.set_value('include_in_ibf', 0);
    }
    frm.refresh_field('include_in_ibf');
  });
}
