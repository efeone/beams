frappe.ui.form.on('Department', {
    onload: function(frm) {
      frm.set_query('cost_center', function() {
          return {
              filters: [
                  ['Cost Center', 'name', 'not in', get_used_cost_centers()]
              ]
          };
      });
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

function get_used_cost_centers() {
    let used_cost_centers = [];

    // Fetch departments that have already selected cost centers
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Department',
            fields: ['cost_center'],
            filters: {
                cost_center: ['is', 'set']
            }
        },
        async: false,
        callback: function(response) {
            used_cost_centers = response.message.map(department => department.cost_center);
        }
    });

    return used_cost_centers;
}




// frappe.ui.form.on('Department', {
//     validate: function(frm) {
//         // Check if the selected cost center is already used
//         let cost_center = frm.doc.cost_center;
//         if (cost_center) {
//             frappe.call({
//                 method: 'frappe.client.get_list',
//                 args: {
//                     doctype: 'Department',
//                     fields: ['name'],
//                     filters: {
//                         cost_center: cost_center
//                     }
//                 },
//                 async: false,
//                 callback: function(response) {
//                     if (response.message.length > 0) {
//                         frappe.msgprint({
//                             title: __('Cost Center already used'),
//                             message: __('The selected cost center is already assigned to another department: {0}', [response.message[0].name]),
//                             indicator: 'red'
//                         });
//                         frappe.validated = false; // Prevent form submission
//                     }
//                 }
//             });
//         }
//     }
// });
