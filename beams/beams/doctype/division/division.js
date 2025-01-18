// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Division', {
    onload: function(frm) {
        get_used_cost_centers(function(cost_centers) {
            // Set query on 'cost_center' field once cost centers are fetched
            frm.set_query('cost_center', function() {
                return {
                    filters: [
                        ['Cost Center', 'name', 'not in', cost_centers],
                        ['Cost Center', 'is_group', '=', 0]
                    ]
                };
            });
        });
    }
});

function get_used_cost_centers(callback) {
    frappe.call({
        method: 'beams.beams.doctype.division.division.get_used_cost_centers',
        callback: function(response) {
            if (response.message) {
                const used_cost_centers = response.message;
                if (callback) {
                    callback(used_cost_centers);
                }
            } else {
                if (callback) {
                    callback([]);
                }
            }
        },
        error: function(error) {
            console.error('Error fetching used cost centers:', error);
        }
    });
}
