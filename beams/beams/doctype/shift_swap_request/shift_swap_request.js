// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Swap Request', {
    refresh: function(frm) {
        // Set the dynamic filter for the 'Swap With Employee' field
        frm.fields_dict['swap_with_employee'].get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    'department': doc.department // Filter employees based on the department field
                }
            };
        };
    }
});
