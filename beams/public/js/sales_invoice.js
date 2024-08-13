frappe.ui.form.on('Sales Invoice', {
  onload: function(frm) {
    frm.toggle_display('actual_customer', false);
    frm.toggle_display('actual_customer_group', false);
    frm.trigger('customer');
  },
  customer: function(frm) {
    if (frm.doc.customer) {
      frappe.db.get_value('Customer', frm.doc.customer, ['is_agent'], function(value) {
        if (value && value.is_agent) {
          frm.toggle_display('actual_customer', true);
          frm.set_value('actual_customer', '');
          frm.toggle_display('actual_customer_group', false);

          if (!frm.doc.is_barter_invoice) {
            frm.set_value('include_in_ibf', 1);
          }
        } else {
          frm.toggle_display('actual_customer', false);
          frm.toggle_display('actual_customer_group', false);
          frm.set_value('include_in_ibf', 0);
        }
        frm.refresh_field('actual_customer');
      });
    } else {
      frm.toggle_display('actual_customer', false);
      frm.toggle_display('actual_customer_group', false);
      frm.set_value('include_in_ibf', 0);
    }
  },
  actual_customer: function(frm) {
    if (frm.doc.actual_customer) {
      frappe.db.get_value('Customer', frm.doc.actual_customer, 'customer_group', function(response) {
        if (response && response.customer_group) {
          frm.toggle_display('actual_customer_group', true);
          frm.set_value('actual_customer_group', response.customer_group);
        } else {
          frm.set_value('actual_customer_group', '');
          frm.toggle_display('actual_customer_group', false);
        }
      });
    } else {
      frm.set_value('actual_customer_group', '');
      frm.toggle_display('actual_customer_group', false);
    }
  },
  is_barter_invoice: function(frm) {
    frm.set_value('include_in_ibf', 0);
    frm.trigger('customer');
  }
});
