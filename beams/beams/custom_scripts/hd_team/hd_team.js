frappe.ui.form.on('HD Team', {
    refresh(frm) {
        apply_filters(frm);
    }
});

function apply_filters(frm) {
    frm.set_query('escalation_to', () => {
        return {
            filters: {
                is_l2_user: 1
            }
        };
    });
}