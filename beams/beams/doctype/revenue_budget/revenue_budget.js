// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on("Revenue Budget", {
    onload: function (frm) {
      set_filters(frm);
    },
    company: function (frm) {
        set_filters(frm);
    }
});
function set_filters(frm) {
    frm.set_query("account", "revenue_accounts", function (doc, cdt, cdn) {
        return {
            filters: {
                company: frm.doc.company
            }
        };
    });
  }

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
    },
    revenue_centre: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        let revenue_centres = frm.doc.revenue_accounts.map(r => r.revenue_centre);
        if (revenue_centres.filter(rc => rc === row.revenue_centre).length > 1) {
            frappe.msgprint(__('Revenue Centre {0} is already selected. Please choose a different one.', [row.revenue_centre]));
            frappe.model.set_value(cdt, cdn, 'revenue_centre', '');
        }
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
