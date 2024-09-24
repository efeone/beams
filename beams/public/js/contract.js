frappe.ui.form.on('Contract', {
    refresh: function(frm) {
        set_item_query(frm);
        calculate_total_amount(frm);
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
    item: function(frm, cdt, cdn) {
        set_item_query(frm, cdt, cdn);
    },
    quantity: function(frm, cdt, cdn) {
        calculate_item_amount(frm, cdt, cdn);
        calculate_total_amount(frm);
    },
    rate: function(frm, cdt, cdn) {
        calculate_item_amount(frm, cdt, cdn);
        calculate_total_amount(frm);
    }
});

// Set query to filter items based on maintain stock
function set_item_query(frm) {
    frm.fields_dict['services'].grid.get_field("item").get_query = function(doc, cdt, cdn) {
        return {
            filters: {
                'is_stock_item': 0  // Only service items
            }
        };
    };
}

// Function to calculate the 'amount' for each row based on 'quantity' and 'rate'
function calculate_item_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.quantity && row.rate) {
        // Calculate the amount: quantity * rate
        row.amount = flt(row.quantity) * flt(row.rate);
        frm.refresh_field('services');  // Refresh the child table to reflect the new amount
    }
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

    // Update only if value is not set or calculated total is different from existing
    if (!frm.doc.total_amount || frm.doc.total_amount !== total) {
        frm.set_value('total_amount', total);
    }
}
