frappe.ui.form.on('Department', {
    onload: function(frm) {
      get_used_cost_centers(function(cost_centers) {
           // Set query on 'cost_center' field once cost centers are fetched
           frm.set_query('cost_center', function() {
               return {
                   filters: [
                       ['Cost Center', 'name', 'not in', cost_centers]
                   ]
               };
           });
       });
        // Fetch users with role 'Hod' based on the department
        frappe.call({
            method: 'beams.beams.custom_scripts.department.department.get_hod_users', // Path to your server-side method
            args: {
                department_name: frm.doc.name // Pass the department name
            },
            callback: function(r) {
                if (r.message) {
                    // Set the query again to include only HOD users
                    frm.set_query('head_of_department', function() {
                        return {
                            filters: {
                                department: frm.doc.name, // Adjust to match the Employee's department field
                                user_id: ['in', r.message || []] // Filter for users with role 'HOD'
                            }
                        };
                    });
                }
            }
        });
    }
});

function get_used_cost_centers(callback) {
    frappe.call({
        method: 'beams.beams.custom_scripts.department.department.get_used_cost_centers',
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
get_used_cost_centers(function(cost_centers) {
});
