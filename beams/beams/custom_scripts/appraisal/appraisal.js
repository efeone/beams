frappe.ui.form.on('Appraisal', {
    refresh: function (frm) {
        frm.remove_custom_button(__('View Goals'));
        // Remove the button by targeting its full class list
        setTimeout(() => {
            $('.new-feedback-btn.btn.btn-sm.d-inline-flex.align-items-center.justify-content-center.px-3.py-2.border').remove();
        }, 500);

        if (!frm.is_new()) {
            // Add custom button to trigger the feedback dialog
            frm.add_custom_button(__('New Feedback'), function () {
                frm.events.show_feedback_dialog(frm);
            });
        }

        if (frm.doc.name) {
            // Check if appraisal_template is set before calling get_appraisal_summary
            if (frm.doc.appraisal_template) {
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
                $(frm.fields_dict['appraisal_summary'].wrapper).html('<p>No Employee Performance Feedback is found.</p>');
            }
        } else {
            $(frm.fields_dict['appraisal_summary'].wrapper).html('<p>Please save the Appraisal to view the summary.</p>');
        }

        // Add Custom Button for One to One Meeting
        if (frm.doc.employee) {
        // Always add the custom button
        frm.add_custom_button(__('One to One Meeting'), function () {
            // Directly map appraisal to event without checking Employee Performance Feedback
            frappe.model.open_mapped_doc({
                method: "beams.beams.custom_scripts.appraisal.appraisal.map_appraisal_to_event", // Mapping method
                args: { source_name: frm.doc.name },
                frm: frm
            });

            // Call assign tasks sequentially function after mapping
            frappe.call({
                method: "beams.beams.custom_scripts.appraisal.appraisal.assign_tasks_sequentially",
                args: {
                    doc: frm.doc.name
                }
            });
        }, __('Create'));
    }

        frappe.call({
            method: "beams.beams.custom_scripts.appraisal.appraisal.get_categories_table",
            callback: function (res) {
                if (res.message) {
                    frm.set_df_property('category_html', 'options', res.message);
                } else {
                    frm.set_df_property('category_html', 'options', '<p>No categories found.</p>');
                }
            }
        });

        // Dynamically add the "Add Category" button only once
        if (!frm.category_button_added) {
            const button_html = `
                <button class="btn btn-primary" id="add_category_button" style="margin-top: 10px;">Add Category</button><br><br>
            `;
            $(frm.fields_dict['category_html'].wrapper).after(button_html);
            frm.category_button_added = true;

            // Button click event for adding a category
            $('#add_category_button').on('click', function () {
                frm.events.open_add_category_dialog(frm);
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
                        },
                        {
                          label:'Weightage(%)',
                          fieldname:'per_weightage',
                          fieldtype:'Percent',
                          in_list_view: 1,
                          reqd: 1,
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
                        },
                        {
                          label:'Weightage(%)',
                          fieldname:'per_weightage',
                          fieldtype:'Percent',
                          in_list_view: 1,
                          reqd: 1,
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
                        },
                        {
                          label:'Weightage(%)',
                          fieldname:'per_weightage',
                          fieldtype:'Percent',
                          in_list_view: 1,
                          reqd: 1,
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
                    frappe.call({
                        method: "beams.beams.custom_scripts.appraisal.appraisal.create_employee_feedback",
                        args: {
                            data: values,
                            appraisal_name: frm.doc.name,
                            employee: frm.doc.employee,
                        },
                        callback: function () {
                            frappe.msgprint(__('Feedback has been submitted successfully.'));
                            frm.refresh();
                            dialog.hide();
                        }
                    });
                }
            },
        });

        dialog.show();
    },
    // Function to open the Add Category dialog
    open_add_category_dialog: function (frm) {
        const dialog = new frappe.ui.Dialog({
            title: 'Add Category',
            fields: [
                { label: 'Select Category', fieldname: 'select_category', fieldtype: 'Link', options: 'Category', only_select: 1, reqd: 1 },
                { label: 'Remarks', fieldname: 'remarks', fieldtype: 'Text', reqd: 1 },
            ],
            primary_action_label: 'Submit',
            primary_action: function (data) {
                if (data.select_category && data.remarks) {
                    let user_id = frappe.session.user;
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: { doctype: "Employee", filters: { user_id: user_id }, fields: ["name", "designation"] },
                        callback: function (response) {
                            if (response.message && response.message.length > 0) {
                                let employee_doc = response.message[0];
                                frappe.call({
                                    method: "beams.beams.custom_scripts.appraisal.appraisal.add_to_category_details",
                                    args: {
                                        parent_docname: frm.doc.name,
                                        category: data.select_category,
                                        remarks: data.remarks,
                                        employee: employee_doc.name,
                                        designation: employee_doc.designation,
                                    },
                                    callback: function (res) {
                                        if (res.message) {
                                            frappe.msgprint(__('Category successfully added to Category Details.'));
                                            frm.reload_doc();
                                            dialog.hide();
                                        } else {
                                            frappe.msgprint(__('Failed to add category.'));
                                        }
                                    },
                                });
                            } else {
                                frappe.msgprint(__('Employee details not found for the logged-in user.'));
                            }
                        },
                    });
                } else {
                    frappe.msgprint(__('Please fill all mandatory fields.'));
                }
            },
        });

        dialog.show();
    },
});
