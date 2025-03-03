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
    },
    onload: function(frm) {
        frm.set_query('revenue_centre', 'revenue_accounts', function(doc, cdt, cdn) {
            return {
                filters: {
                    company: doc.company
                }
            };
        });
    }
});

frappe.ui.form.on('Revenue Account', {
    january: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    february: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    march: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    april: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    may: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    june: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    july: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    august: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    september: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    october: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    november: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    },
    december: function (frm, cdt, cdn) {
        calculate_revenue_amount(frm, cdt, cdn);
    }
});

function calculate_revenue_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    // Calculate the total of all monthly amounts
    let total =
        (row.january || 0) +
        (row.february || 0) +
        (row.march || 0) +
        (row.april || 0) +
        (row.may || 0) +
        (row.june || 0) +
        (row.july || 0) +
        (row.august || 0) +
        (row.september || 0) +
        (row.october || 0) +
        (row.november || 0) +
        (row.december || 0);

    frappe.model.set_value(cdt, cdn, 'revenue_amount', total);
    frm.refresh_field('revenue_account');
}
