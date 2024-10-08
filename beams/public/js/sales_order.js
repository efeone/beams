frappe.ui.form.on('Sales Order', {
  refresh: function(frm) {
    set_actual_customer_query(frm);
    frm.dashboard.clear_headline();
    //Check Overdue Invoices
    if (frm.doc.customer) {
        frappe.call({
            method: "beams.beams.custom_scripts.sales_order.sales_order.check_overdue_invoices",
            args: {
                customer: frm.doc.customer
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let overdue_invoices = r.message;
                    let message = "<b>Overdue Sales Invoices found:</b><br>";
                    overdue_invoices.forEach(invoice => {
                        message += `<a href="/app/sales-invoice/${invoice.name}" style="color:red;">${invoice.name}</a> - ${invoice.due_date}<br>`;
                    });

                    frm.dashboard.set_headline_alert(message, 'red');
                }
            }
        });
    }

    // Check if the Sales Order is being created from a Quotation (i.e., reference_id is set)
    if (frm.doc.reference_id) {
      frm.set_df_property('customer', 'read_only', 1);
      check_is_agent_from_customer(frm);
    } else {
      check_include_in_ibf(frm);
    }
  },

  sales_type: function(frm) {
    if (frm.doc.sales_type) {
      set_item_code_query(frm);
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
    if (frm.is_new()) {
      if (frm.doc.reference_id) {
        check_is_agent_from_customer(frm);
      } else {
        check_include_in_ibf(frm);
      }
    }
  }
});

// Function to set query for the 'actual_customer' field
function set_actual_customer_query(frm) {
  frm.set_query('actual_customer', function() {
    return {
      filters: {
        'is_agent': 0
      }
    };
  });
}

// Function to set query for 'item_code' field in the 'items' child table based on 'sales_type'
function set_item_code_query(frm) {
  frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
    return {
      filters: {
        'sales_type': frm.doc.sales_type  // Filter item_code based on sales_type
      }
    };
  };
}

// Function to check and set the value of 'include_in_ibf'
function check_include_in_ibf(frm) {
  if (frm.doc.sales_type) {
    frappe.db.get_value('Sales Type', frm.doc.sales_type, 'is_time_sales', function(value) {
      if (value && value.is_time_sales && !frm.doc.is_barter_invoice && frm.doc.is_agent) {
        frm.set_value('include_in_ibf', 1);  // Set 'include_in_ibf' to 1 (true)
      } else {
        frm.set_value('include_in_ibf', 0);  // Set 'include_in_ibf' to 0 (false)
      }
      frm.refresh_field('include_in_ibf');  // Refresh the field to reflect the change
    });
  } else {
    frm.set_value('include_in_ibf', 0);  // Default to 0 if sales_type is not set
    frm.refresh_field('include_in_ibf');
  }
}

// New function to fetch 'is_agent' from the Customer doctype
function check_is_agent_from_customer(frm) {
  if (frm.doc.customer) {
    // Fetch the 'is_agent' field from the Customer doctype
    frappe.db.get_value('Customer', frm.doc.customer, 'is_agent', function(value) {
      if (value && value.is_agent) {
        frm.set_value('is_agent', 1);
      } else {
        frm.set_value('is_agent', 0);
      }
      check_include_in_ibf(frm);
    });
  }
}
