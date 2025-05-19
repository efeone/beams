frappe.ui.form.on('HD Ticket', {
    /**
     * Adds the 'Material Request' button under the 'Create' group
     * if 'spare_part_needed' is checked.
     *Runs when the form loads to show or hide fields based on user role
     */

    // Called when form is loaded
    onload: function(frm) {
        handle_agent_visibility(frm);
    },

    // Called every time the form is refreshed
    refresh: function(frm) {
        handle_agent_visibility(frm);
        if (frm.doc.spare_part_needed) {
            frm.page.set_inner_btn_group_as_primary(__('Create'));
            add_material_request_button(frm);
        }
    },

    // Called when the 'spare_part_needed' checkbox is changed
    spare_part_needed: function(frm) {
        frm.clear_custom_buttons();
        if (frm.doc.spare_part_needed) {
            frm.page.set_inner_btn_group_as_primary(__('Create'));
            add_material_request_button(frm);
        }
    }
});

// Function to show/hide fields based on user's role
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

// Function to add a custom button to create Material Request
function add_material_request_button(frm) {
    frm.add_custom_button(__('Material Request'), function() {
        // Create a new Material Request document
        let mr = frappe.model.get_new_doc('Material Request');

        // Populate the Material Request with items from 'spare_part_item_table'
        (frm.doc.spare_part_item_table || []).forEach(row => {
            let child = frappe.model.add_child(mr, 'Material Request Item', 'items');
            child.item_code = row.item;
            child.qty = row.quantity;
            child.schedule_date = row.required_by;
        });

        frappe.set_route('Form', 'Material Request', mr.name);
    }, __('Create'));
}
