frappe.ui.form.on('Interview Feedback', {
    // The code fetches both expected_skill_set and expected_question_set_in_interview_round
    // from the selected "Interview Round" and dynamically updates the respective tables
    interview_round: function(frm) {
        const interview_round_name = frm.doc.interview_round;
        if (interview_round_name) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Interview Round',
                    name: interview_round_name
                },
                callback: function(response) {
                    const interview_round = response.message;

                    if (interview_round && Array.isArray(interview_round.expected_skill_set)) {
                        frm.clear_table('skill_assessment');
                        
                        interview_round.expected_skill_set.forEach(skill => {
                            const row = frm.add_child('skill_assessment');
                            row.weight = skill.weight;
                        });

                        frm.refresh_field('skill_assessment');
                    } else {
                        frappe.msgprint(__('No expected skill set found for the selected interview round.'));
                    }

                    if (interview_round && Array.isArray(interview_round.expected_question_set_in_interview_round)) {
                        frm.clear_table('interview_question_result');
                        
                        interview_round.expected_question_set_in_interview_round.forEach(question => {
                            const row = frm.add_child('interview_question_result');
                            row.weight = question.weight;
                        });

                        frm.refresh_field('interview_question_result');
                    } else {
                        frappe.msgprint(__('No expected question set found for the selected interview round.'));
                    }
                },
                error: function(error) {
                    frappe.msgprint(__('Failed to fetch Interview Round details. Please try again.'));
                }
            });
        }
    }
});
