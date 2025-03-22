frappe.ui.form.on("Training Feedback", {
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
