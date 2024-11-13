frappe.ui.form.on('Employee', {
    /*
    * When the form is refreshed, this script checks if the logged-in user has the "HOD" role
    * and if they have an associated Employee record. If both conditions are met, a custom
    * "Event" button is added to the form.
    */
    refresh: function(frm) {
        if (frappe.user.has_role("HOD")) {
            frappe.call({
                method: "beams.beams.custom_scripts.employee.employee.get_employee_name_for_user",
                args: {
                    user_id: frappe.session.user
                },
                callback: function(response) {
                    if (response.message) {
                        frm.add_custom_button(__('Event'), function() {
                            frappe.model.open_mapped_doc({
                                method: "beams.beams.custom_scripts.employee.employee.create_event",
                                frm: frm,
                                args: {
                                    "employee_id": frm.doc.name,
                                    "hod_user": frappe.session.user
                                }
                            });
                        }, __('Create'));
                     }
                }
            });
        }
    }
});
