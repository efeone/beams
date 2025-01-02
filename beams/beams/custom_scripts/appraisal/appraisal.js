frappe.ui.form.on('Appraisal', {
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.employee) {
            // Fetch `reports_to` and check if logged-in user matches
            frappe.db.get_value('Employee', frm.doc.employee, 'reports_to').then((result) => {
                let reports_to_employee = result.message.reports_to;

                if (reports_to_employee) {
                    frappe.db.get_value('Employee', reports_to_employee, 'user_id').then((user_result) => {
                        let reports_to_user = user_result.message.user_id;

                        if (reports_to_user === frappe.session.user) {
                            frm.add_custom_button(__('New Feedback'), function () {
                                frm.events.show_feedback_dialog(frm);
                            });
                        }
                    });
                }
            });
        }

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

        // Add Custom Button for One to One Meeting
        if (frm.doc.docstatus === 1 && frm.doc.employee) {
            frappe.db.get_value('Employee Performance Feedback',
                { employee: frm.doc.employee, docstatus: 1 },
                'feedback'
            ).then(response => {
                if (response && response.message && response.message.feedback) {
                    frm.add_custom_button(__('One to One Meeting'), function () {
                        frappe.model.open_mapped_doc({
                            method: "beams.beams.custom_scripts.appraisal.appraisal.map_appraisal_to_event",
                            frm: frm
                        });
                    }, __('Create'));
                }
            });
        }
    },

    show_feedback_dialog: function (frm) {
        let dialog = new frappe.ui.Dialog({
            title: 'New Feedback',
            fields: [
                {
                    label: 'Feedback',
                    fieldname: 'feedback',
                    fieldtype: 'Text Editor', // For richer feedback
                    reqd: true,
                    enable_mentions: true,
                },
                {
                    label: 'Employee Criteria',
                    fieldname: 'employee_criteria',
                    fieldtype: 'Table',
                    fields: [
                        {
                            label: 'Criteria',
                            fieldname: 'criteria',
                            fieldtype: 'Link',
                            options: 'Employee Feedback Criteria',
                            in_list_view: 1,
                            reqd: 1,
                        },
                        {
                            label: 'Marks',
                            fieldname: 'marks',
                            fieldtype: 'Float',
                            in_list_view: 1,
                            reqd: 1,
                            description: 'Enter Marks (0 - 5)',
                        }
                    ],
                },
                {
                    label: 'Department Criteria',
                    fieldname: 'department_criteria',
                    fieldtype: 'Table',
                    fields: [
                        {
                            label: 'Criteria',
                            fieldname: 'criteria',
                            fieldtype: 'Link',
                            options: 'Employee Feedback Criteria',
                            in_list_view: 1,
                            reqd: 1,
                        },
                        {
                            label: 'Marks',
                            fieldname: 'marks',
                            fieldtype: 'Float',
                            in_list_view: 1,
                            reqd: 1,
                            description: 'Enter Marks (0 - 5)',
                        }
                    ],
                },
                {
                    label: 'Company Criteria',
                    fieldname: 'company_criteria',
                    fieldtype: 'Table',
                    fields: [
                        {
                            label: 'Criteria',
                            fieldname: 'criteria',
                            fieldtype: 'Link',
                            options: 'Employee Feedback Criteria',
                            in_list_view: 1,
                            reqd: 1,
                        },
                        {
                            label: 'Marks',
                            fieldname: 'marks',
                            fieldtype: 'Float',
                            in_list_view: 1,
                            reqd: 1,
                            description: 'Enter Marks (0 - 5)',
                        }
                    ],
                },
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                // Validate Marks (should be between 0 and 5)
                const validate_marks = (table) => {
                    let isValid = true;
                    table.forEach(row => {
                        if (row.marks < 0 || row.marks > 5) {
                            frappe.msgprint(__('Marks should be between 0 and 5.'));
                            isValid = false;
                        }
                    });
                    return isValid;
                };

                if (
                    validate_marks(values.employee_criteria) &&
                    validate_marks(values.department_criteria) &&
                    validate_marks(values.company_criteria)
                ) {
                    // Push feedback if all marks are valid
                    if (!frm.doc.feedback_list) {
                        frm.doc.feedback_list = [];
                    }

                    frm.doc.feedback_list.push({
                        feedback: values.feedback,
                        employee_criteria: values.employee_criteria,
                        department_criteria: values.department_criteria,
                        company_criteria: values.company_criteria,
                    });

                    frm.refresh_field('feedback_list');
                    frappe.msgprint(__('Your feedback has been submitted.'));
                    dialog.hide();
                }
            },
        });

        dialog.show();
    },
});
