// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Appraisal', {
    employee_appraisal_template: function (frm) {
        if (frm.doc.employee_appraisal_template) {
            frappe.call({
                method: "beams.beams.doctype.performance_appraisal.performance_appraisal.fetch_kra_data",
                args: {
                    template_name: frm.doc.employee_appraisal_template
                },
                callback: function (r) {
                    if (r.message) {
                        frm.clear_table("employee_kra");
                        r.message.forEach(function (kra) {
                            let row = frm.add_child("employee_kra");
                            row.kra = kra;
                        });
                        frm.refresh_field("employee_kra");
                    }
                }
            });
        }
    },
    department_appraisal_template: function (frm) {
        if (frm.doc.department_appraisal_template) {
            frappe.call({
                method: "beams.beams.doctype.performance_appraisal.performance_appraisal.fetch_kra_data",
                args: {
                    template_name: frm.doc.department_appraisal_template
                },
                callback: function (r) {
                    if (r.message) {
                        frm.clear_table("department_kra");
                        r.message.forEach(function (kra) {
                            let row = frm.add_child("department_kra");
                            row.parameter_name = kra;
                        });
                        frm.refresh_field("department_kra");
                    }
                }
            });
        }
    },
    company_appraisal_template: function (frm) {
        if (frm.doc.company_appraisal_template) {
            frappe.call({
                method: "beams.beams.doctype.performance_appraisal.performance_appraisal.fetch_kra_data",
                args: {
                    template_name: frm.doc.company_appraisal_template
                },
                callback: function (r) {
                    if (r.message) {
                        frm.clear_table("company_kra");
                        r.message.forEach(function (kra) {
                            let row = frm.add_child("company_kra");
                            row.kra = kra;
                        });
                        frm.refresh_field("company_kra");
                    }
                }
            });
        }
    }
});
