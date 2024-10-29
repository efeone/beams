frappe.ui.form.on('Budget', {
  refresh: function(frm){
    set_filters(frm);
  },
    cost_center: function(frm) {
        // Clear the department field initially
        frm.set_value('department', '');
        // Check if a cost center is selected
        if (frm.doc.cost_center) {
            // Fetch the corresponding department for the selected cost center
            frappe.db.get_value('Department', { 'cost_center': frm.doc.cost_center }, 'name', (r) => {
                if (r && r.name) {
                    // Set the department field with the fetched value
                    frm.set_value('department', r.name);
                } else {
                    // Optionally handle the case where no department is found
                    frappe.msgprint(__('No department found for the selected cost center.'));
                }
            });
        }
    },
    department: function(frm) {
        frm.refresh_field('accounts');

        // Check if a department is selected
        if (frm.doc.department) {
            // Fetch the cost center associated with the selected department
            frappe.db.get_value('Department', { 'name': frm.doc.department }, 'cost_center', (r) => {
                if (r && r.cost_center) {
                    // Set the cost center field with the fetched value
                    frm.set_value('cost_center', r.cost_center);
                } else {
                    // Optionally handle the case where no cost center is found
                    frappe.msgprint(__('No cost center found for the selected department.'));
                }
            });
        }
    }

});

frappe.ui.form.on('Budget Account', {
    cost_subhead: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        console.log(row);
        if (row.cost_subhead) {
            // Fetch the related account and department from the selected cost_subhead
            frappe.db.get_value('Cost Subhead', row.cost_subhead, ['account', 'department'], function(value) {
                if (value) {
                  console.log(value);
                    // Set the account in the child table
                    frappe.model.set_value(cdt, cdn, 'account', value.account);
                    // Set the department in the parent Budget Account doctype
                    frm.set_value('department', value.department);
                }
            });
        }
    }
});

function set_filters(frm){
  frm.set_query('cost_subhead', 'accounts', (doc, cdt, cdn) => {
        var child = locals[cdt][cdn];
        return {
            filters: {
                'department': frm.doc.department || ''
            }
        }
    });
    frm.set_query('department', function() {
          return {
              filters: {
                  'cost_center': frm.doc.cost_center || ''  // Only show departments related to the selected cost center
              }
          };
      });
}
