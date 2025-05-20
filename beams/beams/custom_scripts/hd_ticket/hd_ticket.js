
frappe.ui.form.on('HD Ticket', {
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
            add_material_request_button(frm);
        }
    },

    spare_part_needed(frm) {
        frm.clear_custom_buttons();
        if (frm.doc.spare_part_needed) {
            frm.page.set_inner_btn_group_as_primary(__('Create'));
            add_material_request_button(frm);
        }
    },

    ticket_type(frm) {
        if (!frm.doc.ticket_type) return frm.set_value('agent_group', '');

        frappe.db.get_value('HD Ticket Type', frm.doc.ticket_type, 'team_name')
            .then(r => frm.set_value('agent_group', r.message?.team_name || ''))
            .catch(() => frm.set_value('agent_group', ''));
    }
});

function handle_agent_visibility(frm) {
    if (!frappe.user.has_role('Agent')) {
        const visible_fields = ['subject', 'raised_by', 'description'];
        frm.fields.forEach(field => {
            const name = field.df.fieldname;
            if (name && !['Section Break', 'Column Break'].includes(field.df.fieldtype)) {
                frm.set_df_property(name, 'hidden', !visible_fields.includes(name));
            }
        });
        frm.refresh_fields();
    }
}

function add_material_request_button(frm) {
    frm.add_custom_button(__('Material Request'), function () {
        const mr = frappe.model.get_new_doc('Material Request');
        (frm.doc.spare_part_item_table || []).forEach(row => {
            const item = frappe.model.add_child(mr, 'Material Request Item', 'items');
            item.item_code = row.item;
            item.qty = row.quantity;
            item.schedule_date = row.required_by;
        });
        frappe.set_route('Form', 'Material Request', mr.name);
    }, __('Create'));
}
