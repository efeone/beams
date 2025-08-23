frappe.ui.form.on('HD Ticket', {
    // Called when form is loaded
    onload(frm) {
        if (frm.is_new() && !frm.doc.raised_by) {
            frm.set_value('raised_by', frappe.session.user);
        }
    },

    refresh(frm) {
        frm.clear_custom_buttons();
        handle_agent_visibility(frm);

        if (frm.doc.material_request_needed) {
            add_material_request_button(frm);
        }
    },

    ticket_type(frm) {
        if (!frm.doc.ticket_type) return frm.set_value('agent_group', '');

        frappe.db.get_value('HD Ticket Type', frm.doc.ticket_type, 'team_name')
            .then(r => frm.set_value('agent_group', r.message?.team_name || ''))
            .catch(() => frm.set_value('agent_group', ''));
    },
    
    material_request_needed(frm) {
        frm.clear_custom_buttons();
        if (frm.doc.material_request_needed) {
            add_material_request_button(frm);
        }
    }
});

/*
   Restricts field visibility for users who do not have the "Agent" role.
   Only the defined fields remain visible to non-Agents.
*/
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

/*
  Adds a "Material Request" button under the "Create" group in the form.
  On click, it creates a new "Material Request" document.
  Populates items from the 'spare_part_item_table' child table of HD Ticket.
*/
function add_material_request_button(frm) {
    frm.add_custom_button(__('Material Request'), () => {
        frappe.new_doc('Material Request', {
            items: (frm.doc.spare_part_item_table || []).map(row => ({
                item_code: row.item,
                qty: row.quantity,
                schedule_date: row.required_by
            }))
        });
    }, __('Create'));
}
