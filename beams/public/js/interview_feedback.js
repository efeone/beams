frappe.ui.form.on('Interview Feedback', {
    // The code fetches both expected_skill_set and expected_question_set_in_interview_round
    // from the selected "Interview Round" and dynamically updates the respective tables
    interview_round: function(frm) {
        const interviewRoundName = frm.doc.interview_round;
        if (interviewRoundName) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Interview Round',
                    name: interviewRoundName
                },
                callback: function(response) {
                    const interviewRound = response.message;

                    if (interviewRound && Array.isArray(interviewRound.expected_skill_set)) {
                        frm.clear_table('skill_assessment');
                        
                        interviewRound.expected_skill_set.forEach(skill => {
                            const row = frm.add_child('skill_assessment');
                            row.weight = skill.weight;
                        });

                        frm.refresh_field('skill_assessment');
                    } else {
                        frappe.msgprint(__('No expected skill set found for the selected interview round.'));
                    }

                    if (interviewRound && Array.isArray(interviewRound.expected_question_set_in_interview_round)) {
                        frm.clear_table('interview_question_result');
                        
                        interviewRound.expected_question_set_in_interview_round.forEach(question => {
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
