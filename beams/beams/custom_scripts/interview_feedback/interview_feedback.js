frappe.ui.form.on('Interview Feedback', {
    interview_round: function (frm) {
      // fetches both expected_skill_set and expected_question_set_in_interview_round
        if (frm.doc.interview_round) {
            frappe.call({
                method: "beams.beams.custom_scripts.interview_feedback.interview_feedback.fetch_details_from_interview_round",
                args: {
                    interview_round: frm.doc.interview_round
                },
                callback: function (response) {
                    if (!response.exc && response.message) {
                        frm.clear_table("skill_assessment");
                        frm.clear_table("interview_question_result");

                        // Populate Skill Assessment child table
                        if (response.message.skills) {
                            response.message.skills.forEach(skill => {
                                frm.add_child("skill_assessment", {
                                    skill: skill.skill,
                                    weight: skill.weight
                                });
                            });
                        }

                        // Populate Interview Question Result child table
                        if (response.message.questions) {
                            response.message.questions.forEach(question => {
                                frm.add_child("interview_question_result", {
                                    question: question.question,
                                    weight: question.weight
                                });
                            });
                        }
                        frm.refresh_field("skill_assessment");
                        frm.refresh_field("interview_question_result");
                    }
                }
            });
        }
    }
});
