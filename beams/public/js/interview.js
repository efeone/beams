frappe.ui.form.on('Interview', {
    refresh: function (frm) {
        setTimeout(function () {
            if (!frm.is_dirty()) {
                frm.add_custom_button(__('Interview Feedback'), function () {
                    frm.events.show_feedback_dialog(frm);
                });
            } else {
                frm.page.clear_primary_action();
                frm.page.set_primary_action(__('Save'), function () {
                    frm.save();
                });
            }
        }, 500);
    },

    show_feedback_dialog: function (frm) {
        frappe.call({
            method: "hrms.hr.doctype.interview.interview.get_expected_skill_set",
            args: {
                interview_round: frm.doc.interview_round,
            },
            callback: function (r) {
                if (r.message) {
                    let skill_fields = frm.events.get_fields_for_feedback();

                    frappe.call({
                        method: "beams.beams.custom_scripts.interview_round.interview_round.get_expected_question_set",
                        args: {
                            interview_round: frm.doc.interview_round,
                        },
                        callback: function (q) {
                            let question_fields = frm.events.get_fields_for_question_assessment();
                            let show_questions_section = q.message && q.message.length > 0;

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
                                        data: r.message,
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
                                        }
                                    ] : []),
                                    {
                                        fieldname: "remarks",
                                        fieldtype: "Small Text",
                                        label: __("Remarks"),
                                        description: __("Additional comments or feedback.")
                                    },
                                    {
                                        fieldname: "result",
                                        fieldtype: "Select",
                                        options: ["", "Cleared", "Rejected"],
                                        label: __("Result"),
                                        reqd: 1,
                                    },
                                ],
                                size: "large",
                                minimizable: true,
                                static: true,
                                primary_action: function (values) {
                                    // Check if all skill set entries have a valid skill and score
                                    const isValid = values.skill_set.every(skill => skill.skill && skill.score != null && skill.score !== '' && !isNaN(skill.score));

                                    if (!isValid) {
                                        frappe.msgprint(__('Each skill must have a Skill and a valid Score.'));
                                        return; // Stop further execution if validation fails
                                    }

                                    // Submit feedback without converting score to rating
                                    frappe.call({
                                        method: "beams.beams.custom_scripts.interview.interview.create_interview_feedback",
                                        args: {
                                            data: values,
                                            interview_name: frm.doc.name,
                                            interviewer: frappe.session.user,
                                            job_applicant: frm.doc.job_applicant,
                                        },
                                        callback: function () {
                                            frappe.msgprint(__('Feedback submitted successfully.'));
                                            frm.refresh();
                                        },
                                        error: function (err) {
                                            frappe.msgprint(__('Error submitting feedback: {0}', [err.message]));
                                        }
                                    });

                                    d.hide();
                                }

                            });

                            d.show();
                            d.get_close_btn().show();
                        },
                        error: function (err) {
                            frappe.msgprint(__('Error fetching expected questions: {0}', [err.message]));
                        }
                    });
                } else {
                    frappe.msgprint(__('No skill set found.'));
                }
            },
            error: function (err) {
                frappe.msgprint(__('Error fetching skill set: {0}', [err.message]));
            }
        });
    },

    get_fields_for_feedback: function () {
        return [
            {
                fieldtype: "Link",
                fieldname: "skill",
                options: "Skill",  // Ensure "Skill" is a valid DocType
                in_list_view: 1,
                label: __("Skill")
            },
            {
                fieldtype: "Int",
                fieldname: "score", // Keep the field as score in the UI
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
                fieldname: "applicant_answer",
                label: __("Applicant's Answer"),
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
});
