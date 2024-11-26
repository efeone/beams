// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maternity Leave Request', {
    setup: function (frm) {
        // Set filter for employee field to only show Female employees
        frm.set_query('employee', function () {
            return {
                filters: {
                    gender: 'Female'
                }
            };
        });
    },
    birth_count: function(frm) {
        // Check the value of birth_count and set no_of_days accordingly
        if (frm.doc.birth_count === 1 || frm.doc.birth_count === 2) {
            frm.set_value('no_of_days', 180);  // Set no_of_days to 180 if birth_count is 1 or 2
        } else if (frm.doc.birth_count >= 3) {
            frm.set_value('no_of_days', 90);   // Set no_of_days to 90 if birth_count is 3 or more
        }
    }
});
