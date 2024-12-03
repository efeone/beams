frappe.ui.form.on('Interview Feedback', {
    interview_round: function (frm) {
        frappe.call({
            method: 'beams.beams.custom_scripts.interview_feedback.interview_feedback.get_interview_details',
            args: {
                interview_round: frm.doc.interview_round
            },
            callback: function (r) {
                if (r.message) {
                    // Clear and set questions
                    frm.clear_table('interview_question_result');
                    frm.set_value('interview_question_result', r.message.questions);
                    frm.refresh_field('interview_question_result');
                    // Clear and set skill assessments
                    frm.clear_table('skill_assessment');
                    frm.set_value('skill_assessment', r.message.skill_assessment);
                    frm.refresh_field('skill_assessment');
                }
            }
        });
    }
});
