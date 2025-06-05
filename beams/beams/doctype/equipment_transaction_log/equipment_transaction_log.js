// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Transaction Log', {
    refresh(frm) {
        // Hide Return Button in Required Items Detail Child Table
        frm.fields_dict['item_log_details'].grid.toggle_display('return', false);
    },
});
