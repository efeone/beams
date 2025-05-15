frappe.ui.form.on('HD Ticket', {
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

function add_material_request_button(frm) {
    frm.add_custom_button(__('Material Request'), function() {
        let mr = frappe.model.get_new_doc('Material Request');

        (frm.doc.spare_part_item_table || []).forEach(row => {
            let child = frappe.model.add_child(mr, 'Material Request Item', 'items');
            child.item_code = row.item;
            child.qty = row.quantity;
            child.schedule_date = row.required_by;
        });

        frappe.set_route('Form', 'Material Request', mr.name);
    }, __('Create'));
}
