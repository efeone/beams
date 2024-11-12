frappe.ui.form.on('Interview', {
    refresh: function (frm) {
        setTimeout(function () {
            // Remove the HR-provided 'Submit Feedback' button if it exists
            frm.remove_custom_button('Submit Feedback');
        }, 250);

        // Add Interview Feedback button if the document is in draft state
        frappe.db.get_value('Interview Feedback', {interview: frm.doc.name,docstatus:1}, 'name') .then(r => {
         let values = r.message;
         if (frm.doc.docstatus === 0&&!values.name) {
             frm.add_custom_button(__('Interview Feedback'), function () {
                 frm.events.show_feedback_dialog(frm);
             });
         }
       })


        // Manage primary action buttons
        setTimeout(function () {
            if (!frm.is_dirty() && frm.doc.docstatus == 0) {
                frm.page.clear_primary_action();
                frm.page.set_primary_action(__('Submit'), function () {
                    frm.savesubmit();
                });
            } else if (frm.is_dirty() && frm.doc.docstatus == 0) {
                frm.page.clear_primary_action();
                frm.page.set_primary_action(__('Save'), function () {
                    frm.save();
                });
            } else if (frm.doc.docstatus == 1) {
                frm.page.clear_primary_action();
            }
        }, 500);
    },

    show_feedback_dialog: function (frm) {
        // Check for existing feedback
        frappe.call({
            method: "beams.beams.custom_scripts.interview.interview.get_interview_feedback",
            args: {
                interview_name: frm.doc.name
            },
            callback: function (r) {
                let existing_feedback = r.message || null;

                // Fetch expected skill set
                frappe.call({
                    method: "hrms.hr.doctype.interview.interview.get_expected_skill_set",
                    args: {
                        interview_round: frm.doc.interview_round,
                    },
                    callback: function (skill_response) {
                        let skill_fields = frm.events.get_fields_for_feedback();

                        // Fetch expected questions set
                        frappe.call({
                            method: "beams.beams.custom_scripts.interview_round.interview_round.get_expected_question_set",
                            args: {
                                interview_round: frm.doc.interview_round,
                            },
                            callback: function (question_response) {
                                let question_fields = frm.events.get_fields_for_question_assessment();
                                let show_questions_section = question_response.message && question_response.message.length > 0;
                                let d = new frappe.ui.Dialog({
                                    title: __("Submit Feedback"),
                                    fields: [
                                        {
                                            fieldname: "skill_set",
                                            fieldtype: "Table",
                                            label: __("Skill Assessment"),
                                            cannot_add_rows: false,
                                            in_editable_grid: true,
                                            reqd: 1,
                                            fields: skill_fields,
                                            data: existing_feedback?existing_feedback.skill_set:skill_response.message,
                                        },
                                        ...(show_questions_section ? [
                                            {
                                                fieldname: "section_break_1",
                                                fieldtype: "Section Break",
                                                label: __("Interview Questions and Answers")
                                            },
                                            {
                                                fieldname: "question_assessment",
                                                fieldtype: "Table",
                                                label: __("Question Assessment"),
                                                cannot_add_rows: false,
                                                in_editable_grid: true,
                                                reqd: 1,
                                                fields: question_fields,
                                                data: existing_feedback?existing_feedback.question_assessment:question_response.message,
                                            }
                                        ] : []),
                                        {
                                            fieldname: "feedback",
                                            fieldtype: "Small Text",
                                            label: __("Feedback"),
                                            description: __("Additional comments or feedback."),
                                            default: existing_feedback ? existing_feedback.feedback : ""
                                        },
                                        {
                                            fieldname: "result",
                                            fieldtype: "Select",
                                            options: ["", "Cleared", "Rejected"],
                                            label: __("Result"),
                                            reqd: 1,
                                            default: existing_feedback ? existing_feedback.result : ""
                                        },
                                    ],
                                    size: "large",
                                    minimizable: true,
                                    static: true,
                                    primary_action_label: __("Save"),
                                    primary_action: function (values) {
                                        frm.events.save_feedback(frm, values, d,0); // Save as draft
                                    },
                                    secondary_action_label: __("Save and Submit"),
                                    secondary_action: function () {
                                        frm.events.save_feedback(frm, d.get_values(), d,1); // Submit
                                    }
                                });

                                // If existing feedback, populate the fields
                                if (existing_feedback) {
                                    d.set_values({
                                        skill_set: existing_feedback.skill_set || [],
                                        question_assessment: existing_feedback.question_assessment || [],
                                        feedback: existing_feedback.feedback,
                                        result: existing_feedback.result
                                    });
                                }

                                d.show();
                                d.get_close_btn().show();
                            },
                            error: function (err) {
                                frappe.msgprint(__('Error fetching expected questions: {0}', [err.message]));
                            }
                        });
                    },
                    error: function (err) {
                        frappe.msgprint(__('Error fetching skill set: {0}', [err.message]));
                    }
                });
            },
            error: function (err) {
                frappe.msgprint(__('Error fetching existing feedback: {0}', [err.message]));
            }
        });
    },

    get_fields_for_feedback: function () {
        return [
            {
                fieldtype: "Link",
                fieldname: "skill",
                options: "Skill",
                in_list_view: 1,
                label: __("Skill")
            },
            {
                fieldtype: "Int",
                fieldname: "score",
                label: __("Score"),
                in_list_view: 1,
                reqd: 1
            }
        ];
    },

    get_fields_for_question_assessment: function () {
        return [
            {
                fieldtype: "Data",
                fieldname: "question",
                label: __("Question"),
                in_list_view: 1,
                reqd: 1
            },
            {
                fieldtype: "Data",
                fieldname: "answer",
                label: __("Answer"),
                in_list_view: 1,
                reqd: 1
            },
            {
                fieldtype: "Int",
                fieldname: "score",
                label: __("Score"),
                in_list_view: 1,
                reqd: 1
            }
        ];
    },

    save_feedback: function (frm, values, dialog, isSubmit) {
        const isValid = values.skill_set.every(skill => skill.skill && skill.score != null && skill.score !== '' && !isNaN(skill.score));
        if (!isValid) {
            frappe.msgprint(__('Each skill must have a Skill and a valid Score.'));
            return;
        }

        // Call the backend method to save feedback
        frappe.call({
            method: "beams.beams.custom_scripts.interview.interview.create_interview_feedback",
            args: {
                data: values,
                interview_name: frm.doc.name,
                interviewer: frappe.session.user,
                job_applicant: frm.doc.job_applicant,
                submit: isSubmit // Pass the submit flag to Python
            },
            callback: function () {
                frappe.msgprint(__('Feedback saved successfully.'));
                frm.refresh(); // Refresh the form to show changes
                dialog.hide(); // Hide the dialog
            },
            error: function (err) {
                frappe.msgprint(__('Error saving feedback: {0}', [err.message]));
            }
        });
    },
});
