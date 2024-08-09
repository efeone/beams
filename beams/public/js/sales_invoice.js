frappe.ui.form.on('Sales Invoice', {
  // Function triggered on form load
    onload: function(frm) {
      // Hide 'actual_customer' and 'actual_customer_group' fields by default
        frm.toggle_display('actual_customer', false);
        frm.toggle_display('actual_customer_group', false);
    },
    customer: function(frm) {
        if (frm.doc.customer) {
            frappe.db.get_value('Customer', frm.doc.customer, ['is_agent'], function(value) {
                if (value && value.is_agent) {
                    frm.toggle_display('actual_customer', true);
                    frm.set_value('actual_customer', '');
                    frm.toggle_display('actual_customer_group', false);
                } else {
                    frm.toggle_display('actual_customer', false);
                    frm.toggle_display('actual_customer_group', false);
                }
                frm.refresh_field('actual_customer');
            });
        } else {
            frm.toggle_display('actual_customer', false);
            frm.toggle_display('actual_customer_group', false);
        }
    },
    actual_customer: function(frm) {
        if (frm.doc.actual_customer) {
          // Fetch the 'customer_group' of the selected 'actual_customer'
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
    customer: function(frm) {
          if (frm.doc.customer) {
              frappe.db.get_value('Customer', frm.doc.customer, 'territory', (r) => {
                  if (r.territory === 'India' && !frm.doc.is_barter_invoice) {
                      frm.set_value('include_in_ibf', 1);
                  } else {
                      frm.set_value('include_in_ibf', 0);
                  }
              });
          } else {
              frm.set_value('include_in_ibf', 0);
          }
      },
      is_barter_invoice: function(frm) {
          frm.trigger('customer');
      }

});
