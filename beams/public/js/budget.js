frappe.ui.form.on('Budget', {
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
        // Trigger when the department field is updated in the parent doctype
        frm.fields_dict['accounts'].grid.get_field('cost_subhead').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn]; // Current row in the child table
            return {
                filters: {
                    'department': frm.doc.department // Filter cost subhead by the selected department in the parent form
                }
            };
        };
    }
});

frappe.ui.form.on('Budget Account', {
    cost_subhead: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];  // Current row in the child table

        if (row.cost_subhead) {
            // Fetch the related account from the selected cost_subhead
            frappe.db.get_value('Cost Subhead', row.cost_subhead, 'account', function(value) {
                if (value) {
                    frappe.model.set_value(cdt, cdn, 'account', value.account);
                }
            });
        }
    }
});
