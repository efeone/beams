frappe.ui.form.on('Department', {
    onload: function(frm) {
        // Fetch users with role 'Hod' based on the department
        frappe.call({
            method: 'beams.beams.custom_scripts.department.department.get_hod_users', // Path to your server-side method
            args: {
                department_name: frm.doc.name // Pass the department name
            },
            callback: function(r) {
                if (r.message) {
                    // Set the query again to include only Hod users
                    frm.set_query('head_of_department', function() {
                        return {
                            filters: {
                                department: frm.doc.name, // Adjust to match the Employee's department field
                                user_id: ['in', r.message] // Filter for users with role 'Hod'
                            }
                        };
                    });
                }
            }
        });
    }
});
