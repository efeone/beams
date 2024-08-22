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
  customer: function(frm) {
    if (frm.doc.customer) {
      if (!frm.doc.is_barter_invoice) {
        frm.set_value('include_in_ibf', 1);
      } else {
        frm.set_value('include_in_ibf', 0);
      }
    } else {
      frm.set_value('include_in_ibf', 0);
    }
  },
  is_barter_invoice: function(frm) {
    frm.set_value('include_in_ibf', 0);
    frm.trigger('customer');
  }
});
