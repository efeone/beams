// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Technical Support Request', {
    refresh: function(frm) {
        frm.fields_dict['employee'].get_query = function(doc) {
            return {
                filters: {
                    'department': doc.department,
                    'designation': doc.designation
                }
            };
        };
    }
});
