// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beams Accounts Settings', {
    setup: function(frm) {
        // Set query filter for 'doc_type' field in the 'beams_naming_rule' child table
        frm.set_query('doc_type', 'beams_naming_rule', function() {
            return {
                filters: {
                    name: ['in', ['Quotation', 'Sales Order', 'Sales Invoice']]  // Filter for specific doctypes
                }
            };
        });

        // Set query filter for the 'batta_claim_service_item' field
        frm.set_query('batta_claim_service_item', function() {
            return {
                filters: {
                    'is_stock_item': 0  // Filter items where 'maintain_stock' is 0
                }
            };
        });

        // Set query filter for the 'stringer_service_item' field
        frm.set_query('stringer_service_item', function() {
          return {
                filters: {
                    'is_stock_item' : 0  // Filter items where 'maintain_stock' is 0
                  }
                };
              });
    },
    onload: function(frm) {
      /*
      * Set a query filter for the 'default_sales_invoice_print_format' field only the enabled print formats for Sales Invoice is show
      */
        frm.set_query('default_sales_invoice_print_format', function() {
            return {
                filters: {
                    'doc_type': 'Sales Invoice',
                    'disabled': 0
                }
            };
        });
    }
});
