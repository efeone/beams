// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Revenue', {
    revenue_template: function (frm) {
        frm.clear_table('revenue_accounts');
        if (frm.doc.revenue_template) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Revenue Template',
                    name: frm.doc.revenue_template
                },
                callback: function (response) {
                    let revenue_template_items = response.message.revenue_template_item || [];
                    revenue_template_items.forEach(function (item) {
                        let row = frm.add_child('revenue_accounts');
                        row.revenue_centre = item.revenue_centre;
                        row.revenue_group = item.revenue_group;
                        row.revenue_category = item.revenue_category;
                        row.revenue_region = item.revenue_region;
                    });
                    frm.refresh_field('revenue_accounts');
                }
            });
        } else {
            frm.refresh_field('revenue_accounts');
        }
    }
});
