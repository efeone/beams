frappe.ui.form.on('Provident Fund', {
    employee_id: function (frm) {
        if (frm.doc.employee_id) {
            frappe.call({
                method: 'beams.beams.doctype.provident_fund.provident_fund.get_employee_by_name',
                args: {
                    employee_name: frm.doc.employee_name,
                },
                callback: function (r) {
                    if (r.message) {
                        let employee = r.message;

                        if (!frm.doc.employee_name) {
                            frm.set_value('employee_name', employee.employee_name);
                        }
                        frm.set_value('department', employee.department);
                        frm.set_value('designation', employee.designation);
                        frm.set_value('mobile', employee.cell_number);
                        frm.set_value('personal_email', employee.personal_email);
                        frm.set_value('company_email', employee.company_email);
                        frm.set_value('name_of_father', employee.name_of_father);
                        frm.set_value('gender', employee.gender);
                        frm.set_value('user_id', employee.user_id);
                        frm.set_value('date_of_birth', employee.date_of_birth);
                        frm.set_value('current_address', employee.current_address);
                        frm.set_value('permanent_address', employee.permanent_address);
                        frm.refresh_fields();
                    }
                },
            });
        }
    },
});
