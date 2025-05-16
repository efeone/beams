frappe.ui.form.on('HD Ticket', {
  /**
     * Adds the 'Material Request' button under the 'Create' group
     * if 'spare_part_needed' is checked.
     */
    refresh: function(frm) {
        if (frm.doc.spare_part_needed) {
            frm.page.set_inner_btn_group_as_primary(__('Create'));
            add_material_request_button(frm);
        }
    },

    spare_part_needed: function(frm) {
        frm.clear_custom_buttons();
        if (frm.doc.spare_part_needed) {
            frm.page.set_inner_btn_group_as_primary(__('Create'));
            add_material_request_button(frm);
        }
    }
});

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
