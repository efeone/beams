frappe.ui.form.on('Sales Invoice', {
  // Function triggered on form load
    onload: function(frm) {
      // Hide 'actual_customer' and 'actual_customer_group' fields by default
        frm.toggle_display('actual_customer', false);
        frm.toggle_display('actual_customer_group', false);

        // Check the "Is Barter Invoice" checkbox by default when the Sales Invoice is created
        if(frm.is_new()) {
            frm.set_value('is_barter_invoice', 1);
        }
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
    }
    });
