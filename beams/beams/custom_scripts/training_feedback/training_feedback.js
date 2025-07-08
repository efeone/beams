frappe.ui.form.on("Training Feedback", {
    onload(frm) {
        if (!frm.doc.employee) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    if (r.message) frm.set_value('employee', r.message.name);
                });
        }
    },

    training_event: function(frm) {
        if (!frm.doc.training_event) {
            frm.set_query("employee", () => ({}));
            frm.set_value("employee", "");
            frm.refresh_field("employee");
            return;
        }

        frappe.db.get_doc("Training Event", frm.doc.training_event).then(event => {
            let employee_list = (event.employees || []).map(emp => emp.employee);
            frm.set_query("employee", () => ({ filters: { name: ["in", employee_list] } }));
            frm.refresh_field("employee");
        });
    }
});
