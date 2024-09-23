frappe.ui.form.on('Contract', {
    onload: function(frm) {
        calculate_total_amount(frm);
    },
    refresh: function(frm) {
        calculate_total_amount(frm);
        set_item_query(frm);

    },
    services_add: function(frm) {
        calculate_total_amount(frm);
    },
    services_remove: function(frm) {
        calculate_total_amount(frm);
    }
});

// For the Services child table
frappe.ui.form.on('Services', {
    amount: function(frm, cdt, cdn) {
        calculate_total_amount(frm);
    },
    items: function(frm, cdt, cdn) {
        set_item_query(frm, cdt, cdn);
    }
});

// Set query to filter items based on the maintain stock
function set_item_query(frm) {
    frm.fields_dict['services'].grid.get_field("items").get_query = function(doc, cdt, cdn) {
        return {
            filters: {
                'is_stock_item': 0  // Only service items
            }
        };
    };
}

// Function to calculate total amount from Services child table
function calculate_total_amount(frm) {
    let total = 0;
    if (frm.doc.services) {
        frm.doc.services.forEach(function(row) {
            if (row.amount) {
                total += flt(row.amount); // Use flt() for numeric addition
            }
        });
    }
    frm.set_value('total_amount', total);
}
