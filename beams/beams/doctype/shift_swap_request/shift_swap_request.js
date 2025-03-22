// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Swap Request', {
    refresh: function(frm) {
        // Set the dynamic filter for the 'Swap With Employee' field
        frm.fields_dict['swap_with_employee'].get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    'department': doc.department,// Filter employees based on the department field
                    'name': ['!=', doc.employee] // Prevent selecting the same employee

                }
            };
        };
    },
  
    onload: function (frm) {
      // Only fetch employee if the field is not set
      if (!frm.doc.employee) {
        frappe.db.get_value('Employee', { 'user_id': frappe.session.user }, 'name')
        .then(response => {
          if (response.message) {
            frm.set_value('employee', response.message.name);
          }
        });
      }
    }
});
