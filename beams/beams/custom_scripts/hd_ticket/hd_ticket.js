frappe.ui.form.on('HD Ticket', {
    // Called when form is loaded
    onload(frm) {
        if (frm.is_new() && !frm.doc.raised_by) {
            frm.set_value('raised_by', frappe.session.user);
        }
        handle_agent_visibility(frm);
    },

    refresh(frm) {
        handle_agent_visibility(frm);
        frm.clear_custom_buttons();

        if (frm.doc.spare_part_needed) {
            frm.page.set_inner_btn_group_as_primary(__('Create'));
        }
    },

    ticket_type(frm) {
        if (!frm.doc.ticket_type) return frm.set_value('agent_group', '');

        frappe.db.get_value('HD Ticket Type', frm.doc.ticket_type, 'team_name')
            .then(r => frm.set_value('agent_group', r.message?.team_name || ''))
            .catch(() => frm.set_value('agent_group', ''));
    }
});

// Function to show/hide fields based on user's role
function handle_agent_visibility(frm) {
    if (!frappe.user.has_role('Agent')) {
        const visible_fields = ['subject', 'raised_by','raised_for', 'description','ticket_type'];
        frm.fields.forEach(field => {
            const name = field.df.fieldname;
            if (name && !['Section Break', 'Column Break'].includes(field.df.fieldtype)) {
                frm.set_df_property(name, 'hidden', !visible_fields.includes(name));
            }
        });
        frm.refresh_fields();
    }
}

