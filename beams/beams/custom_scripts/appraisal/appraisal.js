frappe.ui.form.on('Appraisal', {
    refresh: function (frm) {
        if (frm.doc.name) {
            // Fetch the Employee Performance Feedback related to the Appraisal
            frappe.call({
                method: "beams.beams.custom_scripts.appraisal.appraisal.get_feedback_for_appraisal",
                args: {
                    appraisal_name: frm.doc.name 
                },
                callback: function (res) {
                    if (res.message) {
                        const employee_feedback = res.message;

                        frappe.call({
                            method: "beams.beams.custom_scripts.appraisal.appraisal.get_appraisal_summary",
                            args: {
                                appraisal_template: frm.doc.appraisal_template,
                                employee_feedback: employee_feedback
                            },
                            callback: function (r) {
                                if (r.message) {
                                    $(frm.fields_dict['appraisal_summary'].wrapper).html(r.message);
                                }
                            }
                        });
                    } else {
                        $(frm.fields_dict['appraisal_summary'].wrapper).html('<p>No Employee Performance Feedback found for this appraisal.</p>');
                    }
                }
            });
        } else {
            $(frm.fields_dict['appraisal_summary'].wrapper).html('<p>Please save the Appraisal to view the summary.</p>');
        }
    }
});
