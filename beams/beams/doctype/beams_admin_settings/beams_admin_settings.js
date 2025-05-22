// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('BEAMS Admin Settings', {
    refresh: function(frm) {
        // Apply filter to the default_employee_payable_account field
        frm.set_query('default_employee_payable_account', function() {
            return {
                filters: {
                    'account_type': 'Receivable'
                }
            };
        });
    }
});
