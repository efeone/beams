frappe.ui.form.on('Sales Invoice', {
    refresh: function (frm) {
        setTimeout(() => {
            frm.remove_custom_button('Delivery', 'Create');
            frm.remove_custom_button('Timesheet', 'Get Items From');
            frm.remove_custom_button('Delivery Note', 'Get Items From');
        }, 500);
        set_actual_customer_query(frm);

        // Check if the Sales Invoice is being created from a Quotation (i.e., reference_id is set)
        if (frm.doc.reference_id) {
            // Make the customer field read-only
            frm.set_df_property('customer', 'read_only', 1);
        }
    },
    sales_type: function (frm) {
        if (frm.doc.sales_type) {
            set_item_code_query(frm);
        }
        check_include_in_ibf(frm);

        // Clear and refresh the items table
        frm.clear_table('items');
        frm.refresh_field('items');
    },

    is_barter_invoice: function (frm) {
        check_include_in_ibf(frm);
    },
    is_agent: function (frm) {
        check_include_in_ibf(frm);
    },
    onload: function (frm) {
        // Check if the Sales Invoice is being created from a Quotation (i.e., reference_id is set)
        if (frm.doc.reference_id) {
            // Make the customer field read-only
            frm.set_df_property('customer', 'read_only', 1);
        }
    }
});

// Function to set query for the 'actual_customer' field
function set_actual_customer_query(frm) {
    frm.set_query('actual_customer', function () {
        return {
            filters: {
                'is_agent': 0
            }
        };
    });
}

// Function to set query for 'item_code' field in the 'items' child table based on 'sales_type'
function set_item_code_query(frm) {
    frm.fields_dict['items'].grid.get_field('item_code').get_query = function (doc, cdt, cdn) {
        return {
            filters: {
                'sales_type': frm.doc.sales_type
            }
        };
    };
}

// Function to check and set the value of 'include_in_ibf'
function check_include_in_ibf(frm) {
    if (frm.is_new()) {
        frappe.db.get_value('Sales Type', frm.doc.sales_type, 'is_time_sales', function (value) {
            if (value && value.is_time_sales && !frm.doc.is_barter_invoice && frm.doc.is_agent) {
                frm.set_value('include_in_ibf', 1);  // Set 'include_in_ibf' to 1 (true)
            } else {
                frm.set_value('include_in_ibf', 0);  // Set 'include_in_ibf' to 0 (false)
            }
            frm.refresh_field('include_in_ibf');  // Refresh the field to reflect the change
        });
    }
}
