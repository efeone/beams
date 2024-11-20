frappe.ui.form.on('Interview Feedback', {
    interview_round: function (frm) {
        frappe.call({
            method: 'beams.beams.custom_scripts.interview_feedback.interview_feedback.get_interview_questions',
            args: {
                interview_round: frm.doc.interview_round
            },
            callback: function (r) {
                frm.clear_table('interview_question_result');
                frm.set_value('interview_question_result', r.message);
                frm.refresh_field('interview_question_result');
            }
        });
    }
});
